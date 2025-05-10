# patentDWH 自然言語クエリ例 / Natural Language Query Examples

patentDWH システムでは、特許データベースに対して自然言語で質問することができます。以下に、各データベースに対して可能な自然言語クエリの例を示します。

With the patentDWH system, you can ask questions about patent databases in natural language. Below are examples of natural language queries possible for each database.

## 一般的な質問タイプ / General Question Types

自然言語クエリ機能では、以下のような質問タイプがサポートされています：

The natural language query feature supports the following types of questions:

- **基本検索 / Basic Search**: 特定の条件に合致する特許を検索
- **出願人分析 / Applicant Analysis**: 特定の出願人（企業など）に関する特許情報
- **技術傾向分析 / Technology Trend Analysis**: 特定の技術分野の傾向や変化
- **時系列分析 / Time Series Analysis**: 特定期間における特許動向
- **特許ファミリー分析 / Patent Family Analysis**: 関連特許のファミリー情報
- **分類コード分析 / Classification Code Analysis**: IPCなどの分類コードに基づく分析
- **統計情報 / Statistical Information**: 数量的な統計情報や集計

## INPIT データベースの質問例 / Example Queries for INPIT Database

```
テック株式会社が出願した特許は何件ありますか？
2022年から2023年の間にAI関連で出願された特許数を教えてください
特許分類コードG06Nに属する特許の出願数の推移を教えてください
発明者「佐藤太郎」が関わった特許を教えてください
ロボット技術に関する特許で、最も多く出願している企業はどこですか？
自動運転技術の特許出願数は年々どのように変化していますか？
量子コンピューティングに関する特許の出願状況を教えてください
2020年以降に登録された医療機器関連の特許を教えてください
```

## Google Patents GCP データベースの質問例 / Example Queries for Google Patents GCP Database

```
日立製作所の出願分野で多いものはなんですか？
ソニーが出願した人工知能関連の特許を教えてください
量子コンピューティング技術の特許で、IBMとGoogleはそれぞれ何件出願していますか？
トヨタが出願した自動運転技術に関する特許は何件ありますか？
半導体製造プロセスに関する特許で、サムスンと台湾TSMCの出願数を比較してください
5Gネットワーク関連の特許出願数の推移を国別に教えてください
カーボンニュートラル技術に関する特許出願数は年々どのように変化していますか？
バイオテクノロジー分野で最も多くの特許を持つ企業トップ5を教えてください
```

## Google Patents S3 データベースの質問例 / Example Queries for Google Patents S3 Database

```
日本の企業による海外特許出願の傾向を分析してください
パナソニックによる米国での特許出願数の推移を教えてください
IPCコードG06Fに属する特許の国別出願数を比較してください
機械学習に関する特許で、日本、米国、中国の出願数を比較してください
自動車メーカー各社の電気自動車関連特許数を比較してください
バイオ医薬品分野における日本企業の国際特許出願状況を教えてください
スマートフォン技術に関する特許訴訟が多い企業はどこですか？
再生可能エネルギーに関する特許出願数の国別推移を教えてください
```

## 高度な分析クエリ / Advanced Analysis Queries

```
AIとブロックチェーンの両方に関連する特許を出願している企業はどこですか？
自動運転技術において、トヨタとテスラの特許ポートフォリオの違いを分析してください
量子暗号技術に関する特許出願数の推移と、主要な出願人を教えてください
医療AI分野において、米国と中国の特許出願傾向の違いを分析してください
カーボンキャプチャー技術の特許で、過去5年間で最も革新的な出願は何ですか？
半導体製造技術において、EUVリソグラフィに関する特許出願の国際的な傾向を分析してください
5G通信規格に関する標準必須特許（SEP）を多く保有している企業はどこですか？
バイオ医薬品分野で、COVID-19関連の特許出願がどのように変化したか分析してください
```

## 技術的な制限事項 / Technical Limitations

1. 自然言語クエリは英語と日本語のみサポートしています
2. 非常に複雑な分析や多段階の比較は、単一のクエリでは難しい場合があります
3. 最新の特許データ（数週間以内）はデータベース更新のタイミングによっては含まれていない場合があります
4. 特定の専門用語や略語は、正確に認識されない場合があります
5. 特許全文の内容に関する詳細な意味解析は現在のところ限定的です

1. Natural language queries are supported only in English and Japanese
2. Very complex analysis or multi-step comparisons may be challenging in a single query
3. The most recent patent data (within a few weeks) may not be included depending on database update timing
4. Specific technical terms or abbreviations may not be recognized accurately
5. Detailed semantic analysis of full patent text is currently limited

## クエリの基本構造 / Basic Query Structure

効果的な自然言語クエリを作成するためのヒント：

Tips for creating effective natural language queries:

- 質問は具体的かつ明確に記述してください
- 検索したい主要な技術用語や企業名を明示的に含めてください
- 時間範囲や地理的範囲を指定すると、より正確な結果が得られます
- 分析の目的（傾向、比較、ランキングなど）を明確に示してください
- 複雑な質問は、いくつかの単純な質問に分割すると良いでしょう

- Make questions specific and clear
- Explicitly include key technical terms or company names you want to search for
- Specifying time ranges or geographic scope will yield more accurate results
- Clearly indicate the purpose of analysis (trend, comparison, ranking, etc.)
- Complex questions may be better split into several simpler questions
