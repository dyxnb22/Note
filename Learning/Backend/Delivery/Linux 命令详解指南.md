# Linux 命令详解指南

## Linux 命令面试速查
面试回答 Linux 命令题时，不要只背命令名，要能说清楚：命令解决什么问题、常用参数是什么、实际排查时如何组合使用。

### 1. 文件与目录操作
- `ls`：`ls -lah` 查看权限、大小、隐藏文件；`ls -lht` 按时间倒序。
- `cd`：`cd -` 在两个目录间快速切换。
- `mkdir`：`mkdir -p project/src/main` 递归创建父目录。
- `cp`：`cp -rp source_dir/ backup_dir/` 复制目录并保留属性。
- `rm`：`rm -i file.txt` 删除前确认；`rm -rf dir/` 强制删除目录，生产慎用。
- `ln`：`ln -s` 创建软链接。

### 2. 文本查看与处理
- `cat`：查看短文件。
- `less`：分页查看大日志。
- `head` / `tail`：看头尾；`tail -f` 实时追日志。
- `grep`：过滤关键字，常用 `-i -n -r -v`。
- `awk`：按列提取、统计。
- `sed`：替换、删除、打印。
- `wc -l`：统计行数。

常见组合：
```bash
tail -f app.log | grep --line-buffered "ERROR"
ps aux | grep java | grep -v grep
grep -rn "timeout" /var/log/
```

### 3. 进程与服务管理
- `ps aux` / `ps -ef`：查看进程快照。
- `top`：动态看 CPU、内存、负载。
- `kill -15`：优雅终止。
- `kill -9`：强制终止，兜底使用。
- `systemctl status nginx`：查看服务状态。

### 4. CPU、内存与磁盘排查
- `free -h`：看内存。
- `df -h`：看磁盘分区使用率。
- `du -h --max-depth=1`：逐层找大目录。
- `uptime`：看 load average。
- `iostat` / `iotop`：看 IO。

### 5. 权限与用户管理
- `chmod 755 script.sh`
- `chmod 644 file.txt`
- `chown -R user:group dir`
- `whoami`
- `id`
- `sudo`

### 6. 网络排查与远程连接
- `ip addr` / `ip route`
- `ping 8.8.8.8`
- `curl -I` / `curl -v`
- `ss -tulnp | grep 8080`
- `ssh user@host -p 22`
- `scp -r dir/ host:/tmp/`

### 7. 管道、重定向与后台执行
- `|`：管道
- `>`：覆盖写入
- `>>`：追加写入
- `2>`：错误输出重定向
- `&`：后台运行
- `nohup java -jar app.jar > app.log 2>&1 &`

### 8. 高频问法
### 如何排查 Linux 服务器磁盘满了？

先用 `df -h` 找到满的挂载点，再用 `du -h --max-depth=1` 逐层定位大目录；必要时用 `lsof | grep deleted` 看是否有文件删了但仍被进程占用。

### 如何查找某个端口被哪个进程占用？

优先使用 `ss -tulnp | grep <port>`，也可以 `lsof -i :<port>`。

### 如何实时查看日志并过滤关键字？

`tail -f app.log | grep --line-buffered "ERROR"`。

### 如何排查 CPU 使用率过高？

先用 `top` 找高 CPU 进程，再结合 `ps -ef`、线程级排查和应用日志继续定位。
