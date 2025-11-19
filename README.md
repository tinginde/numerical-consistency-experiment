# 數值推理一致性實驗
# Numerical Reasoning Consistency Experiment

測試大型語言模型在數值推理任務上的一致性與可靠性

## 專案結構

```
numerical-consistency-experiment/
├── data/                           # 資料目錄
│   ├── questions.json             # 生成的測試問題
│   ├── ground_truth.json          # 正確答案
│   └── responses/                 # API 回應資料
│       └── claude_responses.json
├── results/                        # 結果目錄
│   ├── accuracy_results.csv       # 準確率結果
│   ├── consistency_results.csv    # 一致性結果
│   ├── error_analysis.csv         # 錯誤分析
│   └── experiment_report.json     # 完整實驗報告
├── visualizations/                 # 視覺化圖表
│   └── demo_results.png           # 實驗結果圖表
├── src/                            # 原始碼
│   ├── generate_questions.py      # 問題生成器
│   ├── api_caller.py              # API 呼叫模組
│   └── evaluator.py               # 評估器
├── config.py                       # 配置檔案
├── requirements.txt                # Python 套件清單
├── run_experiment.py               # 主執行腳本
├── demo_experiment.py              # 演示腳本（使用模擬數據）
└── README.md                       # 本檔案
```

## 快速開始

### 1. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 2. 執行演示版本（使用模擬數據）

```bash
python demo_experiment.py
```

這會：
- 載入 10 個測試問題
- 生成模擬的 LLM 回應
- 計算準確率和一致性指標
- 產生視覺化圖表

### 3. 執行真實實驗（需要 API key）

首先設置 API key：

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

然後執行實驗：

```bash
# 預設：10 個問題，每個問題 3 種措辭版本，每個版本重複 3 次
python run_experiment.py --num-questions 10 --num-repetitions 3

# 小規模測試：3 個問題
python run_experiment.py --num-questions 3 --num-repetitions 2
```

## 主要功能

### 1. 問題生成器 (generate_questions.py)

生成四種類型的數學問題：
- **基本算術**: 加減乘除
- **百分比與比例**: 百分比計算
- **單位轉換**: 長度、重量、時間轉換
- **比較與排序**: 數字大小比較

每個問題都有 3 種措辭版本：
- **直接數學表述**: "計算 234 + 567"
- **情境化描述**: "小明有 234 元，媽媽又給他 567 元，他現在有多少錢？"
- **問句變化**: "234 加上 567 等於多少？"

### 2. API 呼叫器 (api_caller.py)

- 統一的 LLM API 呼叫介面
- 支援批次處理
- 自動錯誤處理和重試
- 自動儲存中間結果

### 3. 評估器 (evaluator.py)

計算以下指標：

#### 準確性指標
- 絕對準確率
- 數值誤差
- 錯誤類型分類

#### 一致性指標
- **跨措辭一致性** (Cross-paraphrase Consistency): 相同問題不同措辭的答案一致性
- **重複測試一致性** (Test-retest Consistency): 相同問題重複詢問的答案一致性
- **整體一致性分數** (OCS): 上述兩者的平均

## 實驗結果範例

演示實驗的結果（使用模擬數據）：

```
準確性結果:
  總查詢數: 90
  正確: 83
  錯誤: 7
  無法提取答案: 0
  準確率: 92.22%

一致性結果:
  平均跨措辭一致性: 96.70%
  平均重複測試一致性: 92.22%
  平均整體一致性分數 (OCS): 94.46%
```

## 視覺化

實驗會自動生成包含以下圖表的視覺化：
1. 各類別準確率柱狀圖
2. 各運算類型準確率柱狀圖
3. 一致性指標柱狀圖
4. 回應分布圓餅圖

## 進階使用

### 只生成問題（不執行 API 呼叫）

```bash
python run_experiment.py --skip-queries
```

### 使用現有問題和回應進行分析

```bash
python run_experiment.py --skip-generation --skip-queries
```

### 自訂參數

編輯 `config.py` 來修改：
- 模型名稱
- Temperature 設定
- 問題數量
- 檔案路徑

## 研究問題

本實驗旨在探索：

1. **RQ1**: LLMs 在回答相同數值問題但不同措辭時的一致性如何？
2. **RQ2**: 哪些因素（問題複雜度、數字大小、運算類型）最影響一致性？
3. **RQ3**: 模型對自己答案的信心校準程度如何？
4. **RQ4**: 不同 LLMs 之間的表現差異？

## 未來擴展

- 多語言版本（中文、英文、德文）
- Few-shot prompting 測試
- Chain-of-thought 推理
- Temperature 影響分析
- 更多問題類型（代數、幾何、機率等）

## 技術細節

- **Python 版本**: 3.8+
- **主要依賴**:
  - anthropic: Claude API
  - pandas: 資料處理
  - matplotlib: 視覺化
  - seaborn: 視覺化美化

## 授權

本專案供研究和教育用途使用。

## 作者

Tina - 2025-11-19

## 致謝

感謝 Anthropic 提供 Claude API 和 Claude Code 工具。
