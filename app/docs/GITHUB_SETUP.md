# GitHub Repository 設置指南

## 步驟 1: 建立 GitHub Repository

1. 前往 https://github.com/new
2. Repository name: `adaptive-intelligence-pipeline`
3. Description: `可抽換元件的 AI 資訊整合系統 - 支援多種 LLM、資料來源與輸出格式`
4. 選擇 Public（如果要給面試官看）或 Private
5. **不要**勾選 "Initialize with README"（我們已經有了）
6. 點擊 "Create repository"

---

## 步驟 2: 初始化本地 Git

在專案目錄執行：

```bash
# 初始化 git
git init

# 設定主要分支為 main
git branch -M main

# 加入所有檔案
git add .

# 第一次 commit
git commit -m "feat: Initial commit - Week 1 complete

- FastAPI backend with adapter pattern
- Claude API LLM adapter
- arXiv source adapter
- Console & Notion output adapters
- Full pipeline implementation
- Tests and CI/CD setup
- Comprehensive documentation"

# 連接到遠端 repository（替換成你的 GitHub 用戶名）
git remote add origin https://github.com/你的用戶名/adaptive-intelligence-pipeline.git

# 推送到 GitHub
git push -u origin main
```

---

## 步驟 3: 設定 GitHub Secrets（給 CI/CD 用）

如果你想讓 GitHub Actions 也能跑測試：

1. 前往你的 repo → Settings → Secrets and variables → Actions
2. 新增以下 secrets（選擇性）：
   - `ANTHROPIC_API_KEY` - 你的 Claude API key（如果要測試 LLM 功能）

---

## 步驟 4: 設定 GitHub Pages（選擇性）

如果想展示文件：

1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / `docs`
4. Save

文件會發布在：`https://你的用戶名.github.io/adaptive-intelligence-pipeline`

---

## 步驟 5: 美化 README

GitHub 會自動顯示 README.md，你可以加入：

### Badges（徽章）

在 README 最上方加入：

```markdown
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![CI](https://github.com/你的用戶名/adaptive-intelligence-pipeline/actions/workflows/ci.yml/badge.svg)
```

### Screenshot 或 GIF

如果有 Demo 影片或截圖，加入：

```markdown
## Demo

![Demo](docs/images/demo.gif)
```

---

## 步驟 6: 建立 Release（選擇性）

標記 Week 1 完成：

```bash
git tag -a v1.0.0 -m "Week 1 Release - Core functionality complete"
git push origin v1.0.0
```

在 GitHub 上：
1. 前往 Releases
2. Create a new release
3. 選擇 tag `v1.0.0`
4. 標題: `Week 1 - Core Functionality`
5. 描述參考 WEEK1_SUMMARY.md

---

## 步驟 7: 專案管理（選擇性）

### Projects

建立一個 Project board 追蹤進度：
1. 前往 Projects → New project
2. 選擇 "Board" 模板
3. 建立欄位：To Do, In Progress, Done
4. 加入 Week 2 的任務

### Issues

為每個功能建立 issue：
- #1: 實作 AWS Bedrock adapter
- #2: 實作 NewsAPI source adapter
- #3: 實作 Email output adapter

---

## Git 工作流程建議

### 分支策略

```
main        - 穩定版本
develop     - 開發分支
feature/*   - 功能分支
```

### Commit Message 規範

使用 Conventional Commits：

```
feat: 新功能
fix: Bug 修復
docs: 文件更新
test: 測試相關
refactor: 重構
chore: 雜項（依賴更新等）
```

範例：
```bash
git commit -m "feat(llm): add AWS Bedrock adapter"
git commit -m "docs: update architecture diagram"
git commit -m "test: add integration tests for pipeline"
```

---

## 推薦的 GitHub 設定

### .github/PULL_REQUEST_TEMPLATE.md

```markdown
## 變更說明
<!-- 描述這個 PR 做了什麼 -->

## 相關 Issue
Closes #

## 測試
- [ ] 本地測試通過
- [ ] CI 測試通過
- [ ] 更新了文件

## Checklist
- [ ] Code 遵循專案風格
- [ ] 加入了必要的測試
- [ ] 更新了 README（如果需要）
```

### .github/ISSUE_TEMPLATE/bug_report.md

建立 issue 模板讓別人回報問題。

---

## 推薦的 README 結構（已包含）

✅ 專案標題與簡介
✅ 特色亮點
✅ 快速開始
✅ 架構圖
✅ 使用範例
✅ 技術棧
✅ 部署指南
✅ 貢獻指南
✅ 授權

---

## 面試時展示 GitHub

### 重點展示：

1. **README 第一印象**
   - 清楚的專案說明
   - 視覺化的架構圖
   - 快速開始指南

2. **Code 品質**
   - 清晰的目錄結構
   - 有意義的 commit history
   - CI/CD 通過的綠勾勾

3. **文件完整性**
   - 架構文件
   - API 文件（自動生成）
   - 開發指南

4. **專業性**
   - 有測試
   - 有 CI/CD
   - 有 Docker 支援

---

## 完成！

你的專案現在已經：
- ✅ 在 GitHub 上公開
- ✅ 有完整文件
- ✅ 有 CI/CD pipeline
- ✅ 可以展示給面試官看

**下一步：開始 Week 2 的開發！**
