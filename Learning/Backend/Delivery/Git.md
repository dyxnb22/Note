# Git

## Git 面试最终版
Git 是分布式版本控制系统。它的核心价值是记录代码历史、支持多人协作、支持分支并行开发，并且每个开发者本地都有一份完整仓库历史。

---

## 一、核心概念

### 版本控制有哪些类型？Git 和 SVN 的区别是什么？

版本控制主要分为三类：
- 本地版本控制：只在本机记录文件版本，无法方便地团队协作。
- 集中式版本控制：典型代表是 SVN，代码历史集中存放在中央服务器，开发者需要依赖服务器同步代码。
- 分布式版本控制：典型代表是 Git，每个开发者本地都有完整仓库历史，可以离线提交、查看日志、创建分支。

Git 和 SVN 的核心区别：
- Git 是分布式，SVN 是集中式。
- Git 本地有完整历史，SVN 大部分操作依赖中央服务器。
- Git 分支轻量，适合频繁创建、合并和删除；SVN 分支本质更接近目录复制。
- Git 可以离线 commit，SVN 通常需要连接服务器才能提交。
- Git 更适合现代团队的分支开发、Pull Request / Merge Request 和 CI 流程。

### Git 的工作区、暂存区、本地仓库、远程仓库分别是什么？

Git 常见的四个区域：
- 工作区：当前项目目录中实际看到和编辑的文件。
- 暂存区：也叫 index，用来临时保存下一次要提交的修改。
- 本地仓库：执行 `git commit` 后，提交对象保存的位置，包含完整版本历史。
- 远程仓库：托管在 GitHub、GitLab、Gitee 等平台上的仓库，用于团队同步代码。

常见流转关系：
- `git add`：工作区 -> 暂存区。
- `git commit`：暂存区 -> 本地仓库。
- `git push`：本地仓库 -> 远程仓库。
- `git fetch`：远程仓库 -> 本地远程追踪分支。
- `git pull`：远程仓库 -> 本地当前分支，相当于 `fetch + merge` 或 `fetch + rebase`。

### Git 文件有哪些状态？

Git 文件常见状态：
- Untracked：未跟踪，Git 还没有管理这个文件。
- Modified：已修改，工作区内容和上一次提交不同，但还没放入暂存区。
- Staged：已暂存，已经执行 `git add`，等待提交。
- Committed：已提交，修改已经进入本地仓库。

常用判断命令：
- `git status`：查看文件状态。
- `git diff`：查看工作区和暂存区的差异。
- `git diff --cached`：查看暂存区和最近一次提交的差异。

### git add 和 git commit 分别做了什么？

`git add` 把工作区的修改加入暂存区，表示这些修改准备进入下一次提交。
`git commit` 把暂存区内容生成一次提交，保存到本地仓库历史中。提交后并不会自动同步到远程仓库，还需要执行 `git push`。

一句话总结：`add` 是选择本次要提交什么，`commit` 是真正生成一个版本快照。

### git fetch 和 git pull 的区别是什么？

`git fetch` 只把远程仓库的最新提交下载到本地远程追踪分支，不会直接修改当前工作分支。
`git pull` 会下载远程更新并尝试合并到当前分支。默认相当于：

```bash
git fetch
git merge origin/当前分支
```

也可以配置或使用 rebase 模式：

```bash
git pull --rebase
```

面试回答重点：
- `fetch` 更安全，只更新远程追踪信息。
- `pull` 更方便，但会直接影响当前分支。
- 开发中如果担心冲突，建议先 `git fetch`，再 `git diff` 或 `git log` 查看差异，确认后再 merge 或 rebase。

### git merge 和 git rebase 的区别是什么？

`git merge` 会把两个分支的历史合并起来，必要时产生一个 merge commit。优点是保留真实分支历史，缺点是提交线可能不够线性。

`git rebase` 会把当前分支的提交“搬到”目标分支最新提交之后，让历史看起来像一条直线。优点是历史清晰，缺点是会改写提交历史。

使用建议：
- 自己本地尚未推送的提交，可以用 `rebase` 整理历史。
- 已经推送并被别人基于它开发的公共分支，不要随意 `rebase`，避免改写公共历史。

---

## 二、分支管理

### 为什么 Git 分支很轻量？

Git 分支本质上只是一个指向某个 commit 的可移动指针，不是完整复制一份代码，所以创建、切换、删除分支都很快。

### HEAD 是什么？

HEAD 是当前所在位置的指针，通常指向当前分支，分支再指向某个 commit。切换分支时，本质上就是让 HEAD 指向另一个分支。

### 常见分支命令有哪些？

```bash
git branch                 # 查看本地分支
git branch -a              # 查看所有分支（本地+远程）
git checkout -b dev        # 创建并切换到 dev 分支
git switch -c feature/pay  # 新版写法：创建并切换分支
git checkout main          # 切换到 main
git merge dev              # 合并 dev 到当前分支
git branch -d dev          # 删除已合并分支
git branch -D dev          # 强制删除分支
```

### 什么是快进合并和三方合并？

如果目标分支没有新的提交，直接把指针往前移动，这叫 Fast-forward。
如果两个分支各自都有新提交，就需要找公共祖先做三方合并，通常会生成一个 merge commit。

### 开发中常见分支策略有哪些？

常见有：
- Git Flow：`main`、`develop`、`feature`、`release`、`hotfix`，流程清晰但偏重。
- GitHub Flow：主干 + 短期 feature branch + Pull Request，适合持续交付。
- GitLab Flow：在 GitHub Flow 基础上结合环境分支。

现在很多团队倾向于主干开发或简化版 feature branch 工作流。

---

## 三、回退与撤销

### git reset、git revert、git checkout/restore 有什么区别？

- `git reset`：移动 HEAD/分支指针，可同时影响暂存区和工作区，常用于本地撤销提交。
- `git revert`：生成一个“反向提交”抵消某次提交，适合已经推送到远程的公共历史。
- `git restore`：恢复工作区或暂存区文件到指定状态，是新版更清晰的文件恢复命令。

### `git reset --soft / --mixed / --hard` 区别是什么？

- `--soft`：只回退 commit，保留暂存区和工作区修改。
- `--mixed`：回退 commit，同时清空暂存区，保留工作区修改，默认模式。
- `--hard`：回退 commit、暂存区、工作区，修改会直接丢失。

`--hard` 风险最大，使用前要非常谨慎。

### 如果提交已经推到远程，撤销应该怎么做？

如果是公共分支，通常优先用 `git revert`，因为它不会改写历史，更安全。

如果一定要改写远程历史，需要 `git push --force` 或 `git push --force-with-lease`，但这可能影响其他协作者。

### 误删了分支或 commit，还能找回来吗？

可以尝试用 `git reflog` 查看 HEAD 和分支指针的移动历史，找到对应 commit 后再重新建分支：

```bash
git reflog
git checkout -b rescue <commit_id>
```

---

## 四、冲突处理

### 为什么会产生 merge conflict？

两个分支修改了同一文件的同一区域，Git 无法自动判断保留哪一份，就会产生冲突。

### 冲突一般怎么解决？

流程通常是：
1. `git pull` / `git merge` / `git rebase` 后出现冲突。
2. 打开冲突文件，手动处理 `<<<<<<<`、`=======`、`>>>>>>>` 标记。
3. 运行测试，确认逻辑正确。
4. `git add` 标记冲突已解决。
5. merge 场景下执行 `git commit`；rebase 场景下执行 `git rebase --continue`。

### rebase 冲突和 merge 冲突有什么区别？

本质上都是代码冲突，但 rebase 是“按提交一个个重放”，可能在多个提交上分别出现冲突；merge 通常是在合并时统一处理一次。

---

## 五、远程协作

### origin 是什么？

`origin` 只是远程仓库的默认别名，不是固定关键字，可以改成别的名字，但绝大多数仓库都使用 `origin`。

### 如何查看和管理远程仓库？

```bash
git remote -v
git remote add origin git@github.com:user/repo.git
git remote remove origin
git remote rename origin upstream
```

### 什么是 upstream？

上游分支是当前本地分支默认跟踪的远程分支。设置后可以直接使用 `git pull`、`git push`，不用每次写完整远程分支名。

```bash
git push -u origin main
```

### 推送代码被拒绝，常见原因是什么？

常见原因：
- 远程分支有新提交，本地落后。
- 没有权限。
- 分支保护规则限制直接推送。
- 本地历史和远程历史不兼容（例如强推覆盖风险）。

---

## 六、标签、stash 与子模块

### tag 和 branch 有什么区别？

branch 是可移动指针，会随着新提交继续向前。
tag 通常用于给某个固定版本打标记，例如 `v1.0.0`，默认不移动。

### stash 是做什么的？

`git stash` 用于临时保存当前未提交的修改，适合开发到一半需要临时切分支处理别的事情。

```bash
git stash
git stash list
git stash pop
```

### 什么是 Git 子模块？

子模块允许一个仓库引用另一个仓库的某个提交。适合把公共组件作为独立仓库管理，但维护成本比较高，容易在更新、初始化和递归拉取时踩坑。

---

## 七、常见开发场景

### 场景 1：提交错了但还没 push

```bash
git reset --soft HEAD~1
```

撤销最近一次提交，但保留修改内容，方便重新整理后提交。

### 场景 2：代码写一半要切分支

```bash
git stash
git switch hotfix/login
```

处理完后再回来：

```bash
git switch feature/order
git stash pop
```

### 场景 3：误删分支

```bash
git reflog
git checkout -b restore-branch <commit_id>
```

### 场景 4：想同步远程但不想立刻合并

```bash
git fetch
git log --oneline HEAD..origin/main
```

确认后再决定 merge 还是 rebase。

### 场景 5：想把多个提交整理成一个

```bash
git rebase -i HEAD~3
```

把最近三个提交通过 squash/fixup 合并整理。

---

## 八、常见命令速查

```bash
git init
git clone <repo_url>
git status
git add .
git commit -m "feat: add login api"
git log --oneline --graph --decorate
git diff
git diff --cached
git branch
git switch -c feature/user
git merge feature/user
git pull --rebase
git push origin main
git push -u origin feature/user
git stash
git stash pop
git tag v1.0.0
git reflog
```

---

## 九、面试高频简答

### 为什么 Git 比 SVN 更适合现代团队协作？

因为 Git 是分布式的，本地有完整历史，支持离线提交；分支和合并操作轻量，适合 Pull Request、Code Review、CI/CD 等现代协作模式。

### 为什么不建议对公共分支随便 rebase？

因为 rebase 会改写 commit 历史。如果别人已经基于旧历史开发，再强推后会导致他们的分支出现混乱，需要额外处理同步和冲突。

### git pull --rebase 有什么好处？

它会先拉取远程提交，再把本地提交重放到远程最新提交之后，避免额外的 merge commit，让历史更线性、更整洁。

### 如何恢复误删代码？

先判断丢失发生在哪：
- 工作区误删：可尝试 `git restore <file>`。
- 暂存区或提交后丢失：可通过 `git checkout <commit> -- <file>` 或 `git reflog` 找回。

---

## 十、一段简洁面试回答模板

如果面试官问：“你怎么理解 Git？”

可以这样回答：

Git 是分布式版本控制系统，它把代码历史保存在每个开发者本地，支持离线提交、轻量分支、灵活合并和多人协作。它的核心模型可以理解为工作区、暂存区、本地仓库和远程仓库之间的流转。实际开发中我常用 feature branch + Pull Request 的方式协作，本地提交会通过 rebase 保持历史整洁，公共分支上则尽量避免改写历史。出现误提交、冲突或误删时，也可以通过 reset、revert、reflog、stash 等机制安全处理。
