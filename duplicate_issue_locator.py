import requests
import json
import gensim
from gensim import corpora, models, similarities

def fetch_open_issues(owner, repo):
    """Fetch all open issues from the specified GitHub repository."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues?state=open'
    response = requests.get(url)
    return json.loads(response.text)

def extract_issue_texts(issues):
    """Extract issue titles and descriptions from the list of issues."""
    return [f"{issue['title']} {issue['body']}" for issue in issues]

def create_corpus(issue_texts):
    """Create a dictionary and corpus for similarity computation."""
    dictionary = corpora.Dictionary([gensim.utils.simple_preprocess(text) for text in issue_texts])
    return dictionary, [dictionary.doc2bow(gensim.utils.simple_preprocess(text)) for text in issue_texts]

def compute_similarity_matrix(corpus):
    """Train a TF-IDF model and compute the similarity matrix."""
    tfidf = models.TfidfModel(corpus)
    return similarities.MatrixSimilarity(tfidf[corpus])

def find_duplicate_issues(issues, issue_texts, similarity_threshold=0.8):
    """Find and print duplicate issues based on the similarity threshold."""
    dictionary, corpus = create_corpus(issue_texts)
    index = compute_similarity_matrix(corpus)

    for i, issue1 in enumerate(issues):
        similarities = index[corpus[i]]
        for j, issue2 in enumerate(issues):
            if i != j and similarities[j] > similarity_threshold:
                print(f"Issue {issue1['number']} and Issue {issue2['number']} might be duplicates with a similarity score of {similarities[j]:.2f}", flush=True)

if __name__ == '__main__':
    owner, repo = 'Torantulino', 'Auto-GPT'
    issues = fetch_open_issues(owner, repo)
    issue_texts = extract_issue_texts(issues)
    find_duplicate_issues(issues, issue_texts)
