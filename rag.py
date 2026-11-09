"""晴旅小屋：TF-IDF 文件檢索（無 PyTorch、無 Embedding API）。
執行：python rag.py
"""
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
RULES_PATH = BASE_DIR / 'hotel_rules.txt'


def load_rules(path=RULES_PATH):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'找不到飯店規則文件：{path}')
    chunks = []
    title = None
    lines = []

    def save():
        if title is not None:
            content = '\n'.join(lines).strip()
            if content:
                chunks.append({'title': title, 'content': content,
                               'text': f'{title}\n{content}'})

    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if line.startswith('## '):
            save()
            title = line[3:].strip()
            lines = []
        elif title is not None:
            lines.append(line)
    save()
    if not chunks:
        raise ValueError('找不到有效的規則章節，請確認文件使用 ## 標題。')
    return chunks


class HotelRAG:
    def __init__(self, path=RULES_PATH):
        self.chunks = load_rules(path)
        # 中文採用字元 2~4 gram，避免英文單字斷詞器無法有效處理中文。
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4),
                                          lowercase=True, sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(
            [(chunk['title'] + '。') * 4 + chunk['text'] for chunk in self.chunks]
        )

    def search(self, question, top_k=2, min_score=0.08):
        if not isinstance(question, str) or not question.strip():
            return []
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError('top_k 必須是正整數。')
        if not 0 <= min_score <= 1:
            raise ValueError('min_score 必須介於 0 與 1。')
        query_text = question.strip()
        # 少量領域詞彙擴充，補足 TF-IDF 不理解同義詞的限制。
        if '幾點' in query_text and ('入住' in query_text or '退房' in query_text):
            query_text += ' 入住與退房 入住時間 退房時間'
        query = self.vectorizer.transform([query_text])
        if query.nnz == 0:
            return []
        scores = cosine_similarity(query, self.matrix)[0]
        ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
        return [
            {'title': self.chunks[i]['title'],
             'content': self.chunks[i]['content'],
             'score': round(float(score), 4)}
            for i, score in ranked if score >= min_score
        ][:top_k]


if __name__ == '__main__':
    print('Loading hotel rules...')
    rag = HotelRAG()
    print(f'Loaded {len(rag.chunks)} chunks.')
    for question in ['取消訂房可以免費退款嗎？', '幾點可以入住？', '可以帶寵物嗎？']:
        print(f'\nQuestion: {question}')
        results = rag.search(question)
        if not results:
            print('No matching rules found.')
        for i, item in enumerate(results, 1):
            print(f"Result {i}: {item['title']} (score={item['score']})")
            print(item['content'])
