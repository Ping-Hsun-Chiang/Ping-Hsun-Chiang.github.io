---
title: "Link To Github (Local -> Remote)"
date: 2026-04-22
draft: false
category: "其他"
---

## 背景

以 Windows 電腦及 Windows PowerShell 為例，將流程分為兩個情境：

- **Part 1** — Remote 端**尚未**建立 Repository
- **Part 2** — Remote 端**已**建立 Repository

---

<div class="git-split">
<div class="git-col-card">
<div class="git-col-header">Part 1 — Remote 尚未建立 Repo</div>
<div class="git-col-body">
<div class="git-step"><span class="git-step-num">1</span><div><div class="git-step-title">安裝 GitHub CLI</div><pre><code>winget install --id GitHub.cli
gh --version</code></pre></div></div>
<div class="git-step"><span class="git-step-num">2</span><div><div class="git-step-title">授權登入</div><pre><code>gh auth login</code></pre></div></div>
<div class="git-step"><span class="git-step-num">3</span><div><div class="git-step-title">切換至 Local 資料夾</div><pre><code>cd /your/project/path</code></pre></div></div>
<div class="git-step"><span class="git-step-num">4</span><div><div class="git-step-title">初始化 Git 紀錄</div><pre><code>git init
git add .
git commit -m "Initial commit"
git branch -M main</code></pre></div></div>
<div class="git-step"><span class="git-step-num">5</span><div><div class="git-step-title">建立 Repo 並上傳</div><pre><code>gh repo create project-name --public --source=. --remote=origin --push</code></pre><div class="git-step-note">可替換 <code>--public</code> 為 <code>--private</code></div></div></div>
</div>
</div>
<div class="git-col-card">
<div class="git-col-header">Part 2 — Remote 已建立 Repo</div>
<div class="git-col-body">
<div class="git-step"><span class="git-step-num">1</span><div><div class="git-step-title">切換至 Local 資料夾</div><pre><code>cd /your/project/path</code></pre></div></div>
<div class="git-step"><span class="git-step-num">2</span><div><div class="git-step-title">初始化 Git 儲存庫</div><pre><code>git init</code></pre></div></div>
<div class="git-step"><span class="git-step-num">3</span><div><div class="git-step-title">加入暫存區並提交</div><pre><code>git add .
git commit -m "Initial commit"</code></pre></div></div>
<div class="git-step"><span class="git-step-num">4</span><div><div class="git-step-title">設定主要分支名稱</div><pre><code>git branch -M main</code></pre></div></div>
<div class="git-step"><span class="git-step-num">5</span><div><div class="git-step-title">連結 GitHub Repository</div><pre><code>git remote add origin &lt;repo-url&gt;</code></pre></div></div>
<div class="git-step"><span class="git-step-num">6</span><div><div class="git-step-title">Remote 有既有檔案時</div><pre><code>git pull origin main --allow-unrelated-histories</code></pre><div class="git-step-note">若 Remote 無任何檔案可跳過。<br>執行後進入 Vim：按 <code>Esc</code> → 輸入 <code>:wq</code> → Enter</div></div></div>
<div class="git-step"><span class="git-step-num">7</span><div><div class="git-step-title">Push 到 Remote</div><pre><code>git push -u origin main</code></pre></div></div>
</div>
</div>
</div>
