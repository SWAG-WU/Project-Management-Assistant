# GitHub Actions 定时推送实现步骤

## 方案说明

使用 GitHub Actions 的 schedule 功能，每天定时运行脚本，自动推送任务到飞书。

---

## 步骤 1：创建 GitHub 仓库

1. 在 GitHub 创建新仓库（或使用现有仓库）
2. 将项目代码推送到仓库

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

---

## 步骤 2：配置 GitHub Secrets

在仓库中添加敏感信息（不会暴露在代码中）：

1. 进入仓库页面
2. 点击 Settings → Secrets and variables → Actions
3. 点击 New repository secret
4. 添加以下 secrets：

| Secret 名称 | 值 |
|------------|---|
| `OPENAI_API_KEY` | 你的智谱 API Key |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook URL |
| `GITHUB_TOKEN` | GitHub Token（可选，用于灵感抓取） |

---

## 步骤 3：创建 GitHub Actions 工作流

创建文件：`.github/workflows/daily-push.yml`

```yaml
name: Daily Task Push

on:
  schedule:
    # 每天早上 9:00 (UTC+8 = UTC+0 + 8, 所以 9:00 = 1:00 UTC)
    - cron: '0 1 * * *'
    # 每天晚上 21:00 (UTC+8 = 13:00 UTC)
    - cron: '0 13 * * *'
  workflow_dispatch:  # 允许手动触发

jobs:
  push-tasks:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run morning push
      if: github.event.schedule == '0 1 * * *'
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        OPENAI_BASE_URL: https://open.bigmodel.cn/api/paas/v4/
        OPENAI_MODEL: glm-4-air
        LLM_PROVIDER: openai
        FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
      run: |
        python main.py push morning

    - name: Run evening push
      if: github.event.schedule == '0 13 * * *'
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        OPENAI_BASE_URL: https://open.bigmodel.cn/api/paas/v4/
        OPENAI_MODEL: glm-4-air
        LLM_PROVIDER: openai
        FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
      run: |
        python main.py push evening
```

---

## 步骤 4：数据持久化方案

GitHub Actions 每次运行都是全新环境，需要持久化项目数据。

### 方案 A：使用 Git 提交（推荐）

修改工作流，在推送后自动提交数据文件：

```yaml
    - name: Commit data changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/
        git diff --quiet && git diff --staged --quiet || git commit -m "Update project data [skip ci]"
        git push
```

### 方案 B：使用 GitHub Gist 存储

将项目数据存储在 Gist 中，每次读取和更新。

---

## 步骤 5：测试

1. 提交代码到 GitHub
2. 进入 Actions 页面
3. 点击 "Daily Task Push" → "Run workflow" 手动触发测试
4. 查看运行日志，确认推送成功

---

## 时区说明

GitHub Actions 使用 UTC 时间，需要转换：
- 北京时间 9:00 = UTC 1:00 → cron: '0 1 * * *'
- 北京时间 21:00 = UTC 13:00 → cron: '0 13 * * *'

---

## 注意事项

1. 免费账户每月有 2000 分钟的 Actions 时间
2. 定时任务可能延迟 3-10 分钟执行
3. 数据文件需要提交到仓库才能持久化
4. 建议使用私有仓库保护敏感信息

---

## 完整工作流示例（带数据持久化）

已创建文件：`.github/workflows/daily-push.yml`

---

## 步骤 6：推送到 GitHub

```bash
# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Add GitHub Actions workflow"

# 关联远程仓库
git remote add origin https://github.com/你的用户名/仓库名.git

# 推送
git push -u origin main
```

---

## 步骤 7：配置 Secrets

1. 进入 GitHub 仓库页面
2. Settings → Secrets and variables → Actions
3. 添加以下 secrets：
   - `OPENAI_API_KEY`: `1801fad8070746afb02f779086f34269.huoFMYwUgIJff25i`
   - `FEISHU_WEBHOOK_URL`: `https://open.feishu.cn/open-apis/bot/v2/hook/45eade4d-c96b-4cf9-8b33-a1c2a2018ff3`

---

## 步骤 8：手动测试

1. 进入 Actions 页面
2. 选择 "Daily Task Push"
3. 点击 "Run workflow" → "Run workflow"
4. 查看运行日志
5. 检查飞书是否收到消息

---

## 完成！

定时推送已配置完成，每天会自动：
- 早上 9:00 推送当日任务
- 晚上 21:00 推送进度回顾
