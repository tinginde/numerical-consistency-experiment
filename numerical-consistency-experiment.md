# 實驗 A: 數值推理一致性測試
## Numerical Reasoning Consistency in Large Language Models

**研究者**: Tina  
**日期**: 2025-11-19  
**實驗目標**: 測試大型語言模型在數值推理任務上的一致性與可靠性

---

## 1. 研究動機 (Research Motivation)

從實務觀察中發現，LLMs 在處理數值推理時存在不一致性問題。即使是相同的數學問題，用不同的措辭或呈現方式詢問，模型可能給出不同的答案。這種不一致性對於需要可靠數值計算的應用場景（如醫療、金融）構成潛在風險。

本實驗旨在系統性地量化這種不一致性，並探索：
- 什麼類型的數值問題最容易產生不一致？
- 措辭變化如何影響答案的準確性？
- 不同模型之間的表現差異如何？

---

## 2. 研究問題 (Research Questions)

**RQ1**: LLMs 在回答相同數值問題但不同措辭時的一致性如何？  
**RQ2**: 哪些因素（問題複雜度、數字大小、運算類型）最影響一致性？  
**RQ3**: 模型對自己答案的信心校準程度如何？  
**RQ4**: 不同 LLMs（Claude, GPT-4）之間的表現差異？

---

## 3. 實驗設計 (Experimental Design)

### 3.1 測試問題類型

我們將生成 100 個數學問題，涵蓋以下類別：

#### **類別 1: 基本算術 (Basic Arithmetic)** - 25 題
- 加法：兩位數、三位數、小數
- 減法：含借位、跨零
- 乘法：兩位數 × 兩位數、三位數 × 一位數
- 除法：整除、有餘數、小數結果

範例：
- 直接: "計算 234 + 567"
- 情境: "小明有 234 元，媽媽又給他 567 元，他現在有多少錢？"
- 比較: "234 加上 567，結果是多少？"

#### **類別 2: 百分比與比例 (Percentage & Ratios)** - 25 題
- 百分比計算：折扣、成長率
- 比例問題：速率、濃度
- 分數運算

範例：
- 直接: "800 的 15% 是多少？"
- 情境: "一件原價 800 元的衣服打 85 折，折扣金額是多少？"
- 反向: "如果要從 800 中扣除 15%，應該扣多少？"

#### **類別 3: 單位轉換 (Unit Conversion)** - 25 題
- 長度：公分/公尺/公里
- 重量：公克/公斤
- 時間：秒/分/小時
- 溫度：攝氏/華氏

範例：
- 直接: "2.5 公里等於多少公尺？"
- 情境: "從家裡到學校的距離是 2.5 公里，這等於多少公尺？"
- 比較: "2500 公尺和 2.5 公里哪個比較長？"

#### **類別 4: 比較與排序 (Comparison & Ordering)** - 25 題
- 數字大小比較
- 分數/小數比較
- 多數字排序

範例：
- 直接: "比較 0.8 和 3/4 哪個比較大？"
- 情境: "小華得分 0.8，小明得分 3/4，誰的分數比較高？"
- 選擇: "0.8、3/4、0.75，從小到大排列"

### 3.2 措辭變化策略 (Paraphrasing Strategy)

每個問題會產生 3 種不同的措辭版本：

**Version 1: 直接數學表述 (Direct Mathematical)**
- 簡潔、純數學形式
- 例："計算 45 × 23"

**Version 2: 情境化描述 (Contextualized)**
- 加入日常生活情境
- 例："一盒蛋糕有 23 個，買了 45 盒，總共有幾個蛋糕？"

**Version 3: 問句變化 (Question Variation)**
- 改變問法但保持相同的數學問題
- 例："45 和 23 相乘的結果是什麼？"

### 3.3 測試模型

- **Claude Sonnet 4.5** (主要測試對象)
- **GPT-4** (比較基準，如果 API 可用)
- 其他可用的開源模型（可選）

### 3.4 測試程序

```
對於每個問題：
  1. 生成 3 種措辭版本
  2. 向每個模型發送 3 個版本
  3. 記錄：
     - 模型回答
     - 回答時間
     - 答案是否包含數值
     - 是否有解釋過程
  4. 重複 3 次（檢驗同一模型對同一問題的穩定性）
```

總共測試次數：100 問題 × 3 版本 × 3 重複 × N 模型 = 900+ 次呼叫

---

## 4. 評估指標 (Evaluation Metrics)

### 4.1 準確性 (Accuracy)
- **絕對準確率**: 答案完全正確的比例
- **數值誤差**: 答案與正確答案的差距
- **類型錯誤率**: 例如應該是整數卻給小數

### 4.2 一致性 (Consistency)

#### **跨措辭一致性 (Cross-paraphrase Consistency)**
```
Consistency_paraphrase = (相同答案的版本數) / 3
```
- Score = 1.0: 三種措辭都給相同答案
- Score = 0.67: 兩種措辭給相同答案
- Score = 0.33: 三種答案都不同

#### **重複測試一致性 (Test-retest Consistency)**
```
Consistency_retest = (三次測試中相同答案的次數) / 3
```

#### **整體一致性分數 (Overall Consistency Score, OCS)**
```
OCS = (Consistency_paraphrase + Consistency_retest) / 2
```

### 4.3 信心校準 (Confidence Calibration)
如果模型提供信心分數或確定性表述：
- 分析「高信心」答案的準確率
- 分析「低信心」答案的錯誤率
- 計算 Expected Calibration Error (ECE)

### 4.4 錯誤分析 (Error Analysis)
- **錯誤類型分類**:
  - 計算錯誤（運算過程錯）
  - 理解錯誤（誤解題意）
  - 格式錯誤（答案格式不對）
  - 拒絕回答（說不知道或不確定）

---

## 5. 實驗實施計畫 (Implementation Plan)

### Phase 1: 環境設置 (Day 1)
- [ ] 安裝必要套件 (openai, anthropic, numpy, pandas, matplotlib)
- [ ] 設置 API keys
- [ ] 建立專案資料夾結構

### Phase 2: 資料生成 (Day 1)
- [ ] 實作問題生成器
- [ ] 生成 100 個基礎問題
- [ ] 為每個問題生成 3 種措辭版本
- [ ] 建立正確答案資料庫

### Phase 3: API 呼叫模組 (Day 1-2)
- [ ] 實作 Claude API 呼叫函數
- [ ] 實作 GPT-4 API 呼叫函數（如果可用）
- [ ] 加入錯誤處理和重試機制
- [ ] 加入 rate limiting 控制

### Phase 4: 執行實驗 (Day 2-3)
- [ ] 執行所有測試
- [ ] 即時儲存結果（防止中斷遺失資料）
- [ ] 監控 API 使用量

### Phase 5: 資料分析 (Day 3-4)
- [ ] 計算準確性指標
- [ ] 計算一致性分數
- [ ] 錯誤分類與統計
- [ ] 產生視覺化圖表

### Phase 6: 報告撰寫 (Day 4-5)
- [ ] 整理實驗結果
- [ ] 撰寫發現與討論
- [ ] 準備圖表和表格

---

## 6. 技術架構 (Technical Architecture)

```
project/
├── data/
│   ├── questions.json          # 生成的問題資料
│   ├── ground_truth.json       # 正確答案
│   └── responses/              # API 回應原始資料
│       ├── claude_responses.json
│       └── gpt4_responses.json
├── results/
│   ├── accuracy_results.csv
│   ├── consistency_results.csv
│   └── error_analysis.csv
├── visualizations/
│   ├── accuracy_by_category.png
│   ├── consistency_heatmap.png
│   └── error_distribution.png
├── src/
│   ├── generate_questions.py   # 問題生成器
│   ├── api_caller.py           # API 呼叫模組
│   ├── evaluator.py            # 評估指標計算
│   ├── analyzer.py             # 資料分析
│   └── visualizer.py           # 視覺化工具
├── config.py                   # 配置檔案
├── run_experiment.py           # 主執行腳本
└── requirements.txt            # 相依套件清單
```

---

## 7. 程式碼模組說明

### 7.1 問題生成器 (`generate_questions.py`)

```python
class QuestionGenerator:
    """生成數值推理測試問題"""
    
    def generate_arithmetic_questions(n=25):
        """生成基本算術問題"""
        pass
    
    def generate_percentage_questions(n=25):
        """生成百分比問題"""
        pass
    
    def generate_conversion_questions(n=25):
        """生成單位轉換問題"""
        pass
    
    def generate_comparison_questions(n=25):
        """生成比較問題"""
        pass
    
    def create_paraphrases(question):
        """為單一問題生成 3 種措辭版本"""
        return {
            'direct': "...",
            'contextualized': "...",
            'variation': "..."
        }
```

### 7.2 API 呼叫器 (`api_caller.py`)

```python
class LLMTester:
    """統一的 LLM API 呼叫介面"""
    
    def __init__(self, model_name, api_key):
        self.model_name = model_name
        self.api_key = api_key
    
    def query(self, question, temperature=0.0):
        """發送問題並取得回應"""
        pass
    
    def batch_query(self, questions, repeat=3):
        """批次處理多個問題"""
        pass
```

### 7.3 評估器 (`evaluator.py`)

```python
class ConsistencyEvaluator:
    """計算一致性和準確性指標"""
    
    def calculate_accuracy(responses, ground_truth):
        """計算準確率"""
        pass
    
    def calculate_consistency(responses):
        """計算一致性分數"""
        pass
    
    def analyze_errors(responses, ground_truth):
        """錯誤分析"""
        pass
```

---

## 8. 預期結果與假設 (Expected Results & Hypotheses)

### 假設 1: 一致性與問題複雜度負相關
我們預期越複雜的問題（如多步驟計算）會有較低的一致性分數。

### 假設 2: 情境化描述可能降低準確性
加入情境可能引入額外的理解負擔，導致錯誤率上升。

### 假設 3: 數字大小影響表現
較大的數字或小數運算可能比小整數運算有更多錯誤。

### 假設 4: 模型間差異
不同模型在數值推理上的能力可能有顯著差異。

---

## 9. 潛在挑戰與解決方案

### 挑戰 1: API 呼叫成本
**解決方案**: 
- 先用小樣本測試（10-20 題）
- 優先測試一個模型
- 使用 Claude Code 的 promotional credits

### 挑戰 2: 答案抽取困難
模型回應可能包含解釋，需要抽取數值答案。
**解決方案**: 
- 使用正則表達式抽取數字
- 建立答案解析器
- 人工檢查不確定的案例

### 挑戰 3: 評估標準的邊界情況
例如：「大約 100」vs「100」是否算一致？
**解決方案**: 
- 定義明確的評估規則
- 設置容錯範圍（如 ±0.01）
- 記錄邊界案例供討論

### 挑戰 4: 統計顯著性
樣本數可能不足以得出統計顯著的結論。
**解決方案**: 
- 這是探索性研究，先建立基準
- 未來可擴展到更大規模
- 使用 bootstrap 方法估計信賴區間

---

## 10. 時間規劃 (Timeline)

| 階段 | 時間 | 任務 |
|------|------|------|
| Day 1 (今天) | 3-4 小時 | 環境設置、程式碼框架、小規模測試 |
| Day 2-3 | 4-6 小時 | 執行完整實驗、收集資料 |
| Day 4 | 2-3 小時 | 資料分析、產生圖表 |
| Day 5 | 2-3 小時 | 撰寫實驗報告 |

**總時間投入**: 約 11-16 小時

---

## 11. 可延伸方向 (Future Extensions)

如果初步結果有趣，可以延伸為：

1. **多語言版本**: 中文、英文、德文的跨語言一致性
2. **Few-shot prompting**: 提供範例是否能提升一致性？
3. **Chain-of-thought**: 要求模型展示推理過程的效果
4. **Temperature 影響**: 不同 temperature 設定的影響
5. **Prompt engineering**: 測試不同的 system prompts
6. **Time-series analysis**: 追蹤模型更新後的表現變化

---

## 12. 預期產出 (Expected Outputs)

### 12.1 資料產出
- 完整的測試資料集（可公開分享）
- 模型回應資料庫
- 評估結果 CSV 檔案

### 12.2 分析報告
- 實驗報告（3-5 頁）
- 視覺化圖表（5-10 張）
- 錯誤案例集錦

### 12.3 程式碼
- 完整可重現的實驗程式碼
- 使用說明文件
- 可作為未來研究的基礎框架

### 12.4 應用價值
- 可用於 PhD 申請的 research proposal
- 可寫成 workshop paper 或 technical report
- 展示實證研究能力
- 為 motivation letter 提供具體實例

---

## 13. 立即行動 (Immediate Actions)

**今天使用 Claude Code 完成：**

1. ✅ 建立專案資料夾結構
2. ✅ 實作問題生成器（至少完成基本算術類別）
3. ✅ 實作 Claude API 呼叫模組
4. ✅ 測試 10 個問題的完整流程
5. ✅ 產生初步的一致性分析結果

**成功標準**: 今天結束前有一個可以運作的 prototype，能夠：
- 生成測試問題
- 向 Claude 發送問題
- 收集回應
- 計算基本的一致性分數
- 產生一個簡單的視覺化

---

## 14. 參考資源 (References)

### 相關論文
- "Language Models (Mostly) Know What They Know" - Kadavath et al., 2022
- "Measuring Mathematical Problem Solving With the MATH Dataset" - Hendrycks et al., 2021
- "Faithful Reasoning Using Large Language Models" - Creswell & Shanahan, 2022

### 工具與框架
- Anthropic API Documentation: https://docs.anthropic.com
- OpenAI API Documentation: https://platform.openai.com/docs
- Python libraries: `anthropic`, `openai`, `pandas`, `matplotlib`, `seaborn`

---

## 附錄 A: 問題範例集

### 範例 1: 基本加法
```json
{
  "id": "arith_001",
  "category": "arithmetic",
  "operation": "addition",
  "ground_truth": 801,
  "versions": {
    "direct": "計算 234 + 567",
    "contextualized": "小明有 234 元，媽媽又給他 567 元，他現在有多少錢？",
    "variation": "234 加上 567 等於多少？"
  }
}
```

### 範例 2: 百分比
```json
{
  "id": "percent_001",
  "category": "percentage",
  "ground_truth": 120,
  "versions": {
    "direct": "800 的 15% 是多少？",
    "contextualized": "一件原價 800 元的衣服打 85 折，折扣金額是多少？",
    "variation": "如果要從 800 中扣除 15%，應該扣多少？"
  }
}
```

---

## 聯絡資訊

**研究者**: Tina  
**Email**: [你的 email]  
**期間**: 2025-11-19 開始  
**預計完成**: 2025-11-24

---

**Good luck with your experiment! 🚀**

這個實驗設計既有學術價值，又實際可行，更重要的是能為你的 PhD 申請增添亮點！