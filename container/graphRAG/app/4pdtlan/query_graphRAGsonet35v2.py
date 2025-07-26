import sys
from graph2graphRAG import get_answer

# =========================
# メインスクリプト
# =========================

def main():
    # コマンドライン引数から質問を取得
    if len(sys.argv) < 2:
        print("質問を引数として指定してください。例: python main.py 'あなたの質問'")
        sys.exit(1)

    question = sys.argv[1]  # 引数から質問を取得

    # 質問と回答の取得
    response = get_answer(question)

    # 結果の出力
    print("\n==== 質問 ====")
    print(question)

    print("\n==== 回答 ====")
    print(response["result"])

    print("\n==== ソース ====")
    for i, doc in enumerate(response["source_documents"], 1):
        print(f"[{i}] {doc.page_content}")

if __name__ == "__main__":
    main()

