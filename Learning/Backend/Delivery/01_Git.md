# Git

Git 是分布式版本控制系统。它的核心价值是记录代码历史、支持多人协作、支持分支并行开发，并且每个开发者本地都有一份完整仓库历史。

## 核心概念

## 版本控制有哪些类型？Git 和 SVN 有什么区别？

版本控制主要分为三类：

- 本地版本控制：只在本机记录文件版本，无法方便地团队协作。
- 集中式版本控制：典型代表是 SVN，代码历史集中存放在中央服务器，开发者需要依赖服务器同步代码。
- 分布式版本控制：典型代表是 Git，每个开发者本地都有完整仓库历史，可以离线提交、查看日志和创建分支。

Git 和 SVN 的核心区别：

- Git 是分布式，SVN 是集中式。
- Git 本地有完整历史，SVN 大部分操作依赖中央服务器。
- Git 分支轻量，适合频繁创建、合并和删除；SVN 分支更接近目录复制。
- Git 可以离线 commit，SVN 通常需要连接服务器才能提交。
- Git 更适合现代团队的分支开发、Pull Request / Merge Request 和 CI 流程。

## 工作区、暂存区、本地仓库和远程仓库是什么？

| 区域       | 含义                                                         |
| ---------- | ------------------------------------------------------------ |
| 工作区     | 当前项目目录中实际看到和编辑的文件                           |
| 暂存区     | 也叫 index，用来保存下一次要提交的修改                       |
| 本地仓库   | 执行 git commit 后保存提交对象和完整版本历史的位置          |
| 远程仓库   | 托管在 GitHub、GitLab、Gitee 等平台上的仓库，用于团队同步代码 |

常见流转关系：

- git add：工作区 → 暂存区。
- git commit：暂存区 → 本地仓库。
- git push：本地仓库 → 远程仓库。
- git fetch：远程仓库 → 本地远程追踪分支。
- git pull：下载远程更新，并合并或变基到当前分支。

## Git 文件有哪些状态？

- Untracked：未跟踪，Git 还没有管理这个文件。
- Modified：已修改，工作区内容和上一次提交不同，但还没放入暂存区。
- Staged：已暂存，已经执行 git add，等待提交。
- Committed：已提交，修改已经进入本地仓库。

常用判断命令：

~~~bash
git status
git diff
git diff --cached
~~~

git diff 查看工作区和暂存区的差异；git diff --cached 查看暂存区和最近一次提交的差异。

## git add 和 git commit 分别做了什么？

git add 把工作区修改加入暂存区，表示这些修改准备进入下一次提交。git commit 把暂存区内容生成一次提交，保存到本地仓库历史中；提交后还需要 git push 才会同步到远程。

一句话：add 是选择本次提交什么，commit 是真正生成一个版本快照。

## 什么是 HEAD、main 和 origin/main？

- HEAD：当前所在位置，通常指向当前分支的最新提交。
- main：本地分支。
- origin/main：远程追踪分支，表示上次从远程 origin 获取到的 main 分支状态。

可以简单理解为：HEAD 是“我当前在哪”，main 是“我本地分支在哪”，origin/main 是“远程分支上次同步到本地时在哪”。

## 基础配置

## 新电脑上使用 Git 前需要配置什么？

配置用户名和邮箱：

~~~bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
~~~

查看配置：

~~~bash
git config --global --list
git config --system --list
git config --local --list
~~~

常见额外配置：

~~~bash
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.autocrlf input
~~~

global 是当前用户级配置，local 是当前仓库配置，优先级高于 global。user.name 和 user.email 会写入提交记录。

## SSH Key 如何配置？

生成 SSH Key：

~~~bash
ssh-keygen -t ed25519 -C "你的邮箱"
cat ~/.ssh/id_ed25519.pub
~~~

把公钥复制到 GitHub、GitLab 或 Gitee 的 SSH Keys 设置中，再测试连接：

~~~bash
ssh -T git@github.com
~~~

如果公司环境不支持 SSH，也可以使用 HTTPS 远程地址配合访问令牌。

## .gitignore 有什么用？已经提交过的文件还能忽略吗？

.gitignore 用来声明不需要 Git 跟踪的文件，例如依赖目录、构建产物、日志、环境变量文件：

~~~gitignore
node_modules/
dist/
*.log
.env
.DS_Store
~~~

.gitignore 只对未被跟踪的文件生效。如果文件已经提交过，需要从 Git 跟踪中移除，但保留本地文件：

~~~bash
git rm --cached .env
git commit -m "chore: stop tracking env file"
~~~

## 分支与远程协作

## Git 分支为什么轻量？适合解决什么问题？

Git 分支本质上是指向某个提交对象的指针，创建和切换成本很低。

常见用途：

- 功能开发：feature/login
- Bug 修复：fix/login-error
- 紧急线上修复：hotfix/payment
- 发布准备：release/v1.2.0

典型流程：

~~~bash
git switch -c feature/login
## 开发、提交
git push -u origin feature/login
## 提交 PR/MR，合并到主分支
~~~

## 本地已有项目，第一次推送到远程仓库怎么做？

远程先创建一个空仓库，避免自动初始化 README 造成无关历史；本地执行：

~~~bash
git init
git add .
git commit -m "feat: init project"
git branch -M main
git remote add origin git@github.com:用户名/仓库名.git
git push -u origin main
~~~

-u 会设置当前本地分支和远程分支的上游关系，设置后可以直接使用 git push 和 git pull。

## 日常开发的标准流程是什么？

~~~bash
git switch main
git pull --rebase origin main
git switch -c feature/xxx

## 开发完成后
git status
git diff
git add .
git commit -m "feat: xxx"
git push -u origin feature/xxx
~~~

然后在平台上发起 Pull Request / Merge Request，请求合并到主分支。如果已经在自己的功能分支上开发，开始写代码前可以同步主分支：

~~~bash
git fetch origin
git rebase origin/main
~~~

## fetch、pull、merge 和 rebase 有什么区别？

git fetch 只下载远程最新提交并更新本地远程追踪分支，不直接修改当前工作分支。

git pull 下载远程更新并尝试合并到当前分支，通常相当于：

~~~bash
git fetch
git merge origin/当前分支
~~~

也可以使用：

~~~bash
git pull --rebase
~~~

git merge 会把两个分支的历史合并起来，必要时产生 merge commit；优点是保留真实分支历史，缺点是提交线可能不够线性。

git rebase 会把当前分支提交搬到目标分支最新提交之后，让历史更线性；优点是历史清晰，缺点是会改写提交历史。

使用建议：

- 担心远程更新影响当前工作时，先 fetch，再查看差异后决定 merge 或 rebase。
- 自己本地尚未推送的提交，可以用 rebase 整理历史。
- 已经推送并被别人基于它开发的公共分支，不要随意 rebase。
- 主干合并功能分支时，可采用 merge、squash merge 或 rebase merge，按团队规范执行。

## 什么是冲突？如何解决 Git 冲突？

冲突通常发生在 merge、rebase、pull 或 cherry-pick 时：两个分支修改了同一个文件的同一部分，Git 无法自动判断保留哪一边。

解决步骤：

1. 执行 git status 找到冲突文件。
2. 处理 <<<<<<<、=======、>>>>>>> 标记，保留正确代码。
3. 执行 git add 冲突文件标记已解决。
4. merge 执行 git commit；rebase 执行 git rebase --continue；cherry-pick 执行 git cherry-pick --continue。

放弃操作：

~~~bash
git merge --abort
git rebase --abort
git cherry-pick --abort
~~~

## 远程仓库更新了，但本地也改了代码怎么办？

本地修改未提交且要保留：

~~~bash
git stash push -m "临时保存本地修改"
git pull --rebase origin 当前分支名
git stash pop
~~~

stash pop 冲突时，解决后执行 git add 并提交。

本地修改已经提交：

~~~bash
git fetch origin
git rebase origin/当前分支名
## 解决冲突后
git add .
git rebase --continue
git push
~~~

团队要求保留 merge 记录：

~~~bash
git pull origin 当前分支名
~~~

## 本地提交后 push 失败，提示 rejected / non-fast-forward 怎么办？

原因通常是远程分支有本地没有的新提交，Git 不允许直接覆盖远程历史。

推荐处理：

~~~bash
git fetch origin
git rebase origin/当前分支名
git push
~~~

只有确认要覆盖远程，且该分支没有别人依赖时，才考虑：

~~~bash
git push --force-with-lease
~~~

不要随便使用 git push --force。force-with-lease 也不是绝对安全，执行前仍要确认远程分支状态。

## 写到一半需要临时切分支怎么办？

使用 stash 临时保存现场：

~~~bash
git stash push -m "work in progress"
git switch 其他分支

git switch 原分支
git stash list
git stash pop
~~~

- git stash pop：恢复并删除 stash 记录。
- git stash apply：恢复但保留 stash 记录。
- git stash drop stash@{0}：删除某条 stash。

## 提交与历史整理

## reset、revert、restore 和 checkout 有什么区别？

| 命令     | 作用                                                         | 典型场景                              |
| -------- | ------------------------------------------------------------ | ------------------------------------- |
| reset    | 移动当前分支指针，可影响暂存区和工作区                       | 撤销本地提交、取消暂存                |
| revert   | 创建一个反向提交，不改写已有历史                             | 撤销已经推送到公共分支的提交          |
| restore  | 恢复工作区文件或取消暂存                                     | 新版 Git 中替代部分 checkout 用法     |
| checkout | 旧命令，既能切分支又能恢复文件                               | 兼容旧版本；新版本建议拆成 switch/restore |

新版本更推荐：切分支用 git switch，恢复文件用 git restore。

## 提交错了，怎么撤销？

只修改提交信息：

~~~bash
git commit --amend
~~~

上一次提交漏了文件：

~~~bash
git add 漏掉的文件
git commit --amend --no-edit
~~~

撤销最近一次提交，但保留修改在暂存区：

~~~bash
git reset --soft HEAD~1
~~~

撤销最近一次提交，修改回到工作区：

~~~bash
git reset --mixed HEAD~1
~~~

撤销已经推送到公共远程的提交，推荐使用：

~~~bash
git revert commit_id
git push
~~~

简单记忆：公共历史用 revert，本地未推送历史才考虑 reset。

## reset 的 soft、mixed、hard 有什么区别？

三者都会把当前分支指针移动到目标提交，但对暂存区和工作区的处理不同：

- soft：只回退提交，暂存区和工作区保留，适合撤销 commit 后重新提交。
- mixed：默认模式，回退提交并清空暂存区，修改保留在工作区。
- hard：回退提交、暂存区和工作区，可能丢失未保存修改，危险。

~~~bash
git reset --soft HEAD~1
git reset --mixed HEAD~1
git reset --hard HEAD~1
~~~

## 误删文件或想恢复某个文件怎么办？

恢复工作区文件到最近一次提交：

~~~bash
git restore 文件名
~~~

从指定提交恢复文件：

~~~bash
git restore --source commit_id -- 文件名
~~~

取消暂存：

~~~bash
git restore --staged 文件名
~~~

老版本写法：

~~~bash
git checkout commit_id -- 文件名
~~~

## 如何只提交部分修改？

按文件提交：

~~~bash
git add 文件A 文件B
git commit -m "fix: xxx"
~~~

按代码块交互式选择：

~~~bash
git add -p
git commit -m "fix: xxx"
~~~

git add -p 适合一个文件里同时包含多个不相关修改时使用，可以让提交更干净。

## 如何合并多个零散提交？

本地未推送的提交可以使用交互式 rebase：

~~~bash
git rebase -i HEAD~3
~~~

把后面的提交从 pick 改成 squash 或 fixup，即可合并提交。已经推送到公共分支的提交不要随意改写；自己的功能分支需要强推时使用：

~~~bash
git push --force-with-lease
~~~

## 如何把某个提交复制到当前分支？

使用 cherry-pick：

~~~bash
git cherry-pick commit_id
~~~

适合把某个 bugfix 提交同步到 release 分支，或只拿某几个提交而不是合并整个分支。冲突时解决后执行 git add . 和 git cherry-pick --continue；放弃执行：

~~~bash
git cherry-pick --abort
~~~

## 如何查看谁改了某一行代码？

~~~bash
git blame 文件名
git blame -L 10,30 文件名
~~~

它会显示每一行最后由哪个提交、哪个作者修改，实际工作中用于追踪 bug 来源，不是甩锅工具。

## 如何临时保存补丁或在不同仓库间转移修改？

只转移工作区差异：

~~~bash
git diff > change.patch
git apply change.patch
~~~

如果需要保留提交格式：

~~~bash
git format-patch -1 commit_id
git am 0001-xxx.patch
~~~

## 如何找回误删的分支或误 reset 的提交？

使用 git reflog 查看 HEAD 移动历史：

~~~bash
git reflog
~~~

找到丢失提交的 commit ID 后，可以重新创建分支：

~~~bash
git switch -c recover-branch commit_id
~~~

也可以回到该提交：

~~~bash
git reset --hard commit_id
~~~

reflog 是本地记录，远程仓库不一定有。

## 提交规范

## Conventional Commits 常见类型有哪些？

- feat：新增功能。
- fix：修复问题。
- refactor：重构，不改变外部行为。
- docs：文档变更。
- test：测试变更。
- chore：构建、依赖或工具调整。

示例：

~~~text
feat: add user login
fix: handle empty response
chore: update dependencies
~~~

## 命令速查

## 初始化与基础操作

~~~bash
git init
git clone url
git status
git add .
git add 文件名
git add -p
git commit -m "type: message"
git commit --amend
~~~

## 分支操作

~~~bash
git branch
git branch -r
git branch -a
git branch -vv
git switch 分支名
git switch -c 新分支名
git branch -d 分支名
git branch -D 分支名
git push origin --delete 分支名
~~~

老版本 Git：

~~~bash
git checkout 分支名
git checkout -b 新分支名
~~~

## 远程仓库

~~~bash
git remote -v
git remote add origin url
git remote set-url origin url
git fetch origin
git pull origin 分支名
git pull --rebase origin 分支名
git push origin 分支名
git push -u origin 分支名
~~~

## 差异与历史

~~~bash
git diff
git diff --cached
git diff 分支A..分支B
git log
git log --oneline
git log --graph --oneline --all
git show commit_id
git blame 文件名
git reflog
~~~

## 撤销与恢复

~~~bash
git restore 文件名
git restore --staged 文件名
git reset HEAD 文件名
git reset --soft HEAD~1
git reset --mixed HEAD~1
git reset --hard HEAD~1
git revert commit_id
~~~

## 合并、变基与冲突

~~~bash
git merge 分支名
git merge --abort
git rebase 目标分支
git rebase --continue
git rebase --abort
git cherry-pick commit_id
git cherry-pick --continue
git cherry-pick --abort
~~~

## Stash 临时保存

~~~bash
git stash
git stash push -m "说明"
git stash list
git stash pop
git stash apply stash@{0}
git stash drop stash@{0}
git stash clear
~~~

## 清理与排查

~~~bash
git clean -n
git clean -fd
git reflog
git fsck
~~~

- git clean -n 只预览将删除哪些未跟踪文件。
- git clean -fd 会真正删除未跟踪文件和目录，谨慎使用。
- git reflog 可查看 HEAD 移动历史，常用于找回误删分支或误 reset 的提交。
