# Network

# 网络模型
<details>
<summary>OSI 七层模型</summary>
	从上到下分别是：
	- 应用层：为应用程序提供网络服务，比如 HTTP、DNS、FTP。
	- 表示层：负责数据格式转换、压缩、加密等。
	- 会话层：负责建立、管理和终止会话。
	- 传输层：负责端到端传输，典型协议是 TCP、UDP。
	- 网络层：负责 IP 寻址、路由转发和分片。
	- 数据链路层：负责封帧、MAC 寻址、差错检测。
	- 物理层：负责比特流在网线、光纤、无线信道中的传输。
	面试中通常重点关注应用层、传输层、网络层和数据链路层。
</details>
<details>
<summary>TCP/IP 四层模型</summary>
	- 应用层：HTTP、HTTPS、DNS、FTP、SMTP 等，直接面向应用。
	- 传输层：TCP、UDP，负责进程到进程的通信。
	- 网络层：IP、ICMP、ARP 等，负责寻址和路由。
	- 网络接口层：对应 OSI 的数据链路层和物理层，负责在具体链路上传输数据。
	TCP/IP 模型更贴近实际互联网协议栈，面试中常用它解释一次网络请求的完整链路。
</details>
# 应用层
## HTTP
<details>
<summary>应用层常见协议有哪些</summary>
	- HTTP/HTTPS：Web 请求与响应。
	- DNS：域名解析。
	- FTP/SFTP：文件传输。
	- SMTP/POP3/IMAP：邮件发送与接收。
	- WebSocket：全双工实时通信。
	- RPC/gRPC：服务之间的远程调用。
</details>
<details>
<summary>HTTP 报文结构</summary>
	HTTP 请求报文：
	- 请求行：请求方法、URL/URI、HTTP 版本。
	- 请求头：Host、User-Agent、Content-Type、Cookie 等。
	- 空行：分隔头部和请求体。
	- 请求体：可选，常见于 POST、PUT 等请求。
	HTTP 响应报文：
	- 状态行：HTTP 版本、状态码、状态描述。
	- 响应头：Content-Type、Content-Length、Set-Cookie、Cache-Control 等。
	- 空行：分隔头部和响应体。
	- 响应体：HTML、JSON、图片、文件等实际内容。
</details>
<details>
<summary>HTTP 常见状态码</summary>
	HTTP 状态码分为五类：
	- 1xx：提示信息，表示请求已收到，继续处理。
	- 2xx：成功。
	- 3xx：重定向。
	- 4xx：客户端错误。
	- 5xx：服务端错误。
	常见状态码：
	- 200 OK：请求成功。
	- 206 Partial Content：范围请求成功，常用于断点续传。
	- 301 Moved Permanently：永久重定向。
	- 302 Found：临时重定向。
	- 304 Not Modified：资源未修改，可使用缓存。
	- 400 Bad Request：请求格式错误。
	- 401 Unauthorized：未认证。
	- 403 Forbidden：已认证但无权限。
	- 404 Not Found：资源不存在。
	- 405 Method Not Allowed：请求方法不支持。
	- 500 Internal Server Error：服务端内部错误。
	- 502 Bad Gateway：网关或代理从上游收到无效响应。
	- 503 Service Unavailable：服务暂不可用。
	- 504 Gateway Timeout：网关等待上游超时。
</details>
<details>
<summary>HTTP 常用请求方法及幂等性</summary>
	- GET：获取资源，安全且幂等，可缓存、可收藏为书签。
	- POST：提交数据或创建资源，不安全且通常不幂等。
	- PUT：整体更新资源，不安全但幂等。
	- PATCH：局部更新资源，不安全，是否幂等取决于实现。
	- DELETE：删除资源，不安全但通常幂等。
	- HEAD：只获取响应头，不返回响应体，常用于探测资源元信息。
	- OPTIONS：询问服务器支持的方法，常见于跨域预检请求。
	安全是指不会修改服务端资源；幂等是指执行一次和执行多次的结果一致。
</details>
<details>
<summary>HTTP 长连接是什么</summary>
	HTTP 长连接指多个 HTTP 请求/响应复用同一个 TCP 连接，避免频繁建立和释放 TCP 连接的开销。
	- HTTP/1.0 默认短连接，需要显式使用 `Connection: Keep-Alive` 开启长连接。
	- HTTP/1.1 默认长连接，通常不发送 `Connection: close` 就会保持连接。
	- 长连接不会永久存在，服务器一般会配置空闲超时时间和最大请求数，到达后主动关闭。
</details>
<details>
<summary>HTTP/1.1 如何确定消息体边界</summary>
	HTTP/1.1 常见的消息体边界判断方式有三种：
	- `Content-Length`：头部明确声明 body 字节数，接收方按长度读取。
	- `Transfer-Encoding: chunked`：分块传输，每个 chunk 自带长度，最后以长度为 0 的 chunk 结束。适用于响应或请求体长度一开始未知的场景。
	- 无 body：如果既没有 `Content-Length`，也没有 `Transfer-Encoding`，通常表示没有请求体。
	如果同时出现 `Transfer-Encoding: chunked` 和 `Content-Length`，应以 `Transfer-Encoding` 为准，并忽略 `Content-Length`，否则容易出现请求走私等安全问题。
</details>
<details>
<summary>HTTP 断点续传怎么实现</summary>
	断点续传依赖 HTTP Range 请求：
	1. 服务端返回 `Accept-Ranges: bytes`，表示支持按字节范围请求。
	2. 客户端记录已下载位置，例如已下载 512KB。
	3. 续传时客户端发送 `Range: bytes=512000-`，表示从该位置继续下载。
	4. 服务端返回 `206 Partial Content`，并携带 `Content-Range` 和 `Content-Length`。
	5. 如果请求范围超过资源大小，服务端返回 `416 Requested Range Not Satisfiable`。
	核心头部是 `Range`、`Accept-Ranges`、`Content-Range`、`Content-Length`。
</details>
<details>
<summary>HTTP 为什么不安全</summary>
	HTTP 是明文传输，主要有三类风险：
	- 窃听：中间人可以直接读取通信内容。
	- 篡改：中间人可以修改请求或响应内容。
	- 冒充：客户端无法确认服务端身份，可能访问到伪造网站。
	HTTPS 在 HTTP 和 TCP 之间加入 TLS，通过加密、完整性校验和证书认证解决这些问题。
</details>
<details>
<summary>HTTP 和 HTTPS 的区别</summary>
	<table header-row="true" header-column="false">
<tr>
<td>对比项</td>
<td>HTTP</td>
<td>HTTPS</td>
</tr>
<tr>
<td>安全性</td>
<td>明文传输</td>
<td>TLS 加密传输</td>
</tr>
<tr>
<td>默认端口</td>
<td>80</td>
<td>443</td>
</tr>
<tr>
<td>连接建立</td>
<td>TCP 三次握手后直接传输 HTTP</td>
<td>TCP 三次握手后还要 TLS 握手</td>
</tr>
<tr>
<td>身份认证</td>
<td>无</td>
<td>通过 CA 证书验证服务端身份</td>
</tr>
<tr>
<td>防篡改</td>
<td>无</td>
<td>TLS 消息认证可检测篡改</td>
</tr>
<tr>
<td>性能</td>
<td>开销较低</td>
<td>多 TLS 握手和加解密开销，但可通过会话复用、HTTP/2、HTTP/3 优化</td>
</tr>
	</table>
</details>
<details>
<summary>HTTPS TLS 握手过程</summary>
	以常见 TLS 握手为例，核心流程是：
	1. ClientHello：客户端发送支持的 TLS 版本、随机数 Client Random、加密套件列表。
	2. ServerHello：服务端选择 TLS 版本和加密套件，返回 Server Random，并发送证书。
	3. 证书校验：客户端校验证书链、域名、有效期、是否被吊销等。
	4. 密钥交换：客户端和服务端协商会话密钥。旧的 RSA 流程中，客户端生成 pre-master secret 后用服务端公钥加密发送；现代更常见的是 ECDHE，通过双方临时密钥协商出共享秘密，具备前向安全性。
	5. 生成会话密钥：双方基于 Client Random、Server Random 和共享秘密生成对称加密密钥。
	6. Finished：双方用协商出的密钥发送握手摘要，验证握手过程没有被篡改。
	7. 后续通信：使用对称加密传输 HTTP 数据。
	要点：非对称加密主要用于身份认证和密钥协商，真正传输业务数据时使用对称加密。
</details>
<details>
<summary>HTTPS 如何防范中间人攻击</summary>
	HTTPS 防中间人攻击依赖三点：
	- 证书认证：服务端证书由受信任 CA 签发，客户端会验证证书链、域名、有效期等。攻击者没有合法证书，难以冒充真实服务端。
	- 密钥协商：客户端和服务端协商出只有双方知道的对称密钥。攻击者即使截获握手报文，也无法得到会话密钥。
	- 完整性校验：TLS 会对消息做认证，通信内容被篡改后能被发现。
	注意：HTTPS 不是用服务端公钥加密所有业务数据，而是用非对称机制协商对称密钥，后续用对称加密通信。
</details>
<details>
<summary>HTTP/1.1、HTTP/2、HTTP/3 的区别</summary>
	<table header-row="true" header-column="false">
<tr>
<td>版本</td>
<td>传输基础</td>
<td>主要特性</td>
<td>解决的问题</td>
</tr>
<tr>
<td>HTTP/1.1</td>
<td>TCP</td>
<td>默认长连接、管道化、缓存控制</td>
<td>减少短连接开销，但仍有应用层队头阻塞</td>
</tr>
<tr>
<td>HTTP/2</td>
<td>TCP</td>
<td>二进制帧、多路复用、HPACK 头部压缩、服务端推送</td>
<td>解决 HTTP/1.1 多请求并发效率低的问题，但仍受 TCP 队头阻塞影响</td>
</tr>
<tr>
<td>HTTP/3</td>
<td>UDP + QUIC</td>
<td>QUIC 多路复用、TLS 1.3 内置、连接迁移、0-RTT</td>
<td>解决 TCP 层队头阻塞，弱网和网络切换体验更好</td>
</tr>
	</table>
	HTTP/2 的多路复用是在一条 TCP 连接上并发多个 Stream；如果底层 TCP 丢包，所有 Stream 仍会被阻塞。HTTP/3 基于 QUIC，不同 Stream 可以独立重传，降低队头阻塞影响。
</details>
<details>
<summary>HTTP 连接建立后什么情况下会中断</summary>
	- 任意一端主动关闭连接，发送 FIN，进入四次挥手。
	- 出现异常，发送 RST 强制断开连接。
	- 发送方数据长期得不到 ACK，达到最大重传次数后断开。
	- HTTP 长连接空闲超过服务器配置的 keepalive timeout。
	- HTTP 长连接复用请求数达到上限。
	- 网络故障、进程崩溃、防火墙或负载均衡器清理连接。
</details>
<details>
<summary>HTTP、Socket 和 TCP 的区别</summary>
	- HTTP 是应用层协议，定义请求和响应的语义、报文格式、状态码等。
	- TCP 是传输层协议，提供面向连接、可靠、有序的字节流传输。
	- Socket 是操作系统提供的网络编程接口，不是协议。应用程序通过 Socket 使用 TCP 或 UDP 通信。
	可以理解为：HTTP 通常跑在 TCP 之上，应用程序通过 Socket 调用系统能力完成网络收发。
</details>
## DNS
<details>
<summary>DNS 是什么</summary>
	DNS 是 Domain Name System，用于把域名解析成 IP 地址。默认端口是 53。
	域名层级从右到左逐级降低，例如 `www.server.com`：
	- 根 DNS 服务器：`.`。
	- 顶级域 DNS 服务器：`.com`。
	- 权威 DNS 服务器：`server.com` 的权威记录。
</details>
<details>
<summary>DNS 域名解析流程</summary>
	以 `www.server.com` 为例：
	1. 浏览器、操作系统、hosts、本地 DNS 缓存先查找，命中则直接返回。
	2. 未命中时，客户端请求本地 DNS 服务器。
	3. 本地 DNS 问根 DNS，根 DNS 返回 `.com` 顶级域服务器地址。
	4. 本地 DNS 问 `.com` 顶级域服务器，拿到 `server.com` 权威 DNS 地址。
	5. 本地 DNS 问权威 DNS，拿到 `www.server.com` 的 IP。
	6. 本地 DNS 把结果返回客户端，并按 TTL 缓存。
	7. 客户端用解析出的 IP 建立连接。
	客户端到本地 DNS 通常是递归查询，本地 DNS 到根、顶级、权威 DNS 通常是迭代查询。
</details>
<details>
<summary>DNS 使用 TCP 还是 UDP</summary>
	DNS 查询通常使用 UDP，因为 UDP 无连接、开销小、延迟低，适合短小的域名查询。
	但 DNS 并不是只用 UDP，以下场景会使用 TCP：
	- 响应报文过大，UDP 放不下或被截断。
	- 区域传送，也就是 DNS 服务器之间同步记录。
	- 某些安全或可靠性要求更高的场景。
	DNS 可靠性主要依赖超时重试、缓存和多 DNS 服务器配置。
</details>
<details>
<summary>DNS 劫持是什么，怎么防范</summary>
	DNS 劫持是攻击者篡改 DNS 响应，把用户要访问的域名解析到恶意 IP，导致用户访问假网站或被插入广告。
	防范方式：
	- 使用可信 DNS 服务，避免使用不可信网络提供的 DNS。
	- 使用 DNS over HTTPS 或 DNS over TLS，减少解析过程被篡改。
	- 域名侧开启 DNSSEC，验证 DNS 记录完整性。
	- HTTPS 证书校验能阻止攻击者伪造合法站点。
	- 对核心域名做解析监控，发现异常 IP 及时告警。
</details>
## Web 认证与会话
<details>
<summary>HTTP 是无状态的，Cookie 为什么能保持状态</summary>
	HTTP 无状态是指协议本身不记住上一次请求，每个请求彼此独立。
	Cookie 是 HTTP 之上的状态补充机制：服务端通过 `Set-Cookie` 把会话标识或少量状态写到浏览器，浏览器后续请求自动带上 `Cookie`，服务端就能识别用户。
	所以准确说法是：HTTP 协议本身无状态，但可以借助 Cookie、Session、Token 等机制实现业务层的状态管理。
</details>
<details>
<summary>Cookie、Session、Token、JWT 的区别</summary>
	<table header-row="true" header-column="false">
<tr>
<td>对比项</td>
<td>Cookie</td>
<td>Session</td>
<td>Token</td>
<td>JWT</td>
</tr>
<tr>
<td>存储位置</td>
<td>浏览器</td>
<td>服务端</td>
<td>客户端</td>
<td>客户端</td>
</tr>
<tr>
<td>保存内容</td>
<td>少量键值对</td>
<td>用户会话数据</td>
<td>认证凭证</td>
<td>Header.Payload.Signature</td>
</tr>
<tr>
<td>服务端状态</td>
<td>可有可无</td>
<td>有状态</td>
<td>通常无状态</td>
<td>通常无状态</td>
</tr>
<tr>
<td>请求携带</td>
<td>浏览器自动携带</td>
<td>通常靠 Cookie 传 SessionId</td>
<td>手动放 Header 或 Cookie</td>
<td>手动放 Header 或 Cookie</td>
</tr>
<tr>
<td>优点</td>
<td>简单、自动携带、可设置 HttpOnly/SameSite</td>
<td>敏感数据在服务端，更易管控</td>
<td>适合前后端分离和跨端</td>
<td>自包含、可签名、防篡改</td>
</tr>
<tr>
<td>缺点</td>
<td>容量小，注意 CSRF/XSS</td>
<td>分布式场景需共享 Session</td>
<td>泄露后有风险</td>
<td>签发后失效前难主动撤销</td>
</tr>
	</table>
	Session 适合传统单体或服务端渲染；Token/JWT 更适合前后端分离、移动端、微服务和跨域场景。
</details>
<details>
<summary>客户端禁用 Cookie 后 Session 还能用吗</summary>
	默认不能正常使用。因为大多数 Web 应用依赖 Cookie 保存 SessionId，浏览器禁用 Cookie 后，服务端无法通过请求识别对应 Session。
	替代方案：
	- URL 重写：把 SessionId 放到 URL 中，例如 `;jsessionid=xxx`。缺点是容易泄露，不推荐。
	- 隐藏表单字段：表单提交时携带 SessionId。缺点是只适合表单交互，不适合普通链接和 AJAX。
	- 改用 Token：由客户端在请求头中主动携带认证凭证。
</details>
<details>
<summary>Cookie 和 LocalStorage 有什么区别</summary>
	<table header-row="true" header-column="false">
<tr>
<td>对比项</td>
<td>Cookie</td>
<td>LocalStorage</td>
</tr>
<tr>
<td>容量</td>
<td>约 4KB</td>
<td>通常 5MB 以上</td>
</tr>
<tr>
<td>请求携带</td>
<td>同域请求自动携带</td>
<td>不会自动随请求发送</td>
</tr>
<tr>
<td>生命周期</td>
<td>可设置过期时间</td>
<td>默认长期保存，除非手动清理</td>
</tr>
<tr>
<td>访问方式</td>
<td>服务端和客户端都可用，HttpOnly 后 JS 不可读</td>
<td>只能被前端 JS 读取</td>
</tr>
<tr>
<td>安全风险</td>
<td>需要防 CSRF，非 HttpOnly 时也怕 XSS</td>
<td>主要怕 XSS 读取</td>
</tr>
<tr>
<td>适合场景</td>
<td>会话标识、需要自动随请求发送的数据</td>
<td>本地缓存、非敏感配置、页面状态</td>
</tr>
	</table>
	敏感认证信息更推荐放在 `HttpOnly + Secure + SameSite` 的 Cookie 中，减少被 XSS 直接读取的风险；如果放 LocalStorage，一旦发生 XSS，Token 很容易被盗。
</details>
<details>
<summary>哪些数据适合放 Cookie，哪些适合放 LocalStorage</summary>
	Cookie 适合：
	- SessionId、短期认证凭证。
	- 服务端需要自动随请求接收的数据。
	- 需要设置过期时间、HttpOnly、Secure、SameSite 的数据。
	LocalStorage 适合：
	- 非敏感的用户偏好设置。
	- 前端缓存数据。
	- 页面间共享的本地状态。
	不要把密码、身份证号、银行卡号等敏感明文数据放进 Cookie 或 LocalStorage。
</details>
<details>
<summary>JWT 结构是什么</summary>
	JWT 由三部分组成，用点号分隔：
	- Header：令牌类型和签名算法，例如 `alg`、`typ`。
	- Payload：声明信息，例如用户 ID、角色、过期时间 `exp`。
	- Signature：对 Header 和 Payload 做签名，防止内容被篡改。
	JWT 的 Header 和 Payload 只是 Base64URL 编码，不是加密，不能放敏感明文信息。
</details>
<details>
<summary>JWT 为什么适合集群部署</summary>
	集群部署是指同一个服务部署在多台机器上，由负载均衡把请求分发到不同实例。
	传统 Session 默认存在单台服务器内存中，请求如果打到另一台机器，可能找不到会话，需要 Session 复制、粘性会话或 Redis 共享存储。
	JWT 是自包含的，服务端只要能验证签名，就能从 Token 中解析用户身份和权限，不依赖本机 Session。这样每台服务器都可以独立处理请求，更适合水平扩展和微服务。
</details>
<details>
<summary>JWT 的缺点和泄露处理</summary>
	JWT 的主要缺点：
	- 签发后在过期前默认一直有效，不容易主动撤销。
	- Payload 不能放敏感明文。
	- Token 体积比 SessionId 大，每次请求携带会增加带宽。
	- 如果存储在 LocalStorage，容易被 XSS 窃取；如果存 Cookie，又要防 CSRF。
	泄露后的处理：
	- 缩短 Access Token 有效期。
	- 使用 Refresh Token 续签，并对 Refresh Token 做轮换。
	- 维护黑名单或版本号，让指定 Token 失效。
	- 用户改密、退出登录、发现异常时强制刷新密钥或会话版本。
	- 前端存储时优先考虑 HttpOnly、Secure、SameSite Cookie，并配合 CSRF Token。
</details>
<details>
<summary>前端如何存储 JWT</summary>
	常见方式有三种：
	<table header-row="true" header-column="false">
<tr>
<td>存储方式</td>
<td>优点</td>
<td>风险</td>
</tr>
<tr>
<td>LocalStorage</td>
<td>使用简单，不自动携带，适合前后端分离</td>
<td>XSS 后可被 JS 直接读取</td>
</tr>
<tr>
<td>SessionStorage</td>
<td>关闭标签页后失效</td>
<td>仍然怕 XSS</td>
</tr>
<tr>
<td>Cookie</td>
<td>可自动携带，可设置 HttpOnly/Secure/SameSite</td>
<td>需要防 CSRF</td>
</tr>
	</table>
	面试回答可以说：没有绝对安全的存法，关键是结合 XSS、CSRF 防护。认证 Cookie 建议加 `HttpOnly`、`Secure`、`SameSite`，重要操作再配合 CSRF Token。
</details>
# 传输层
## TCP 基础
<details>
<summary>TCP 头部有哪些关键字段</summary>
	TCP 头部常见关键字段：
	- 源端口、目的端口：标识通信双方进程。
	- 序列号 Seq：标识本报文段第一个字节的序号，用于按序接收、去重和重传。
	- 确认号 Ack：表示期望收到的下一个字节序号，用于确认对方数据。
	- 数据偏移：表示 TCP 头部长度。
	- 控制位：SYN、ACK、FIN、RST、PSH、URG。
	- 窗口大小：用于流量控制，告诉对方自己还能接收多少数据。
	- 校验和：检测 TCP 头部和数据是否出错。
	常见控制位：
	- SYN：建立连接。
	- ACK：确认号有效。
	- FIN：正常关闭连接。
	- RST：异常重置连接。
</details>
<details>
<summary>TCP 和 UDP 的区别</summary>
	<table header-row="true" header-column="false">
<tr>
<td>对比项</td>
<td>TCP</td>
<td>UDP</td>
</tr>
<tr>
<td>连接</td>
<td>面向连接</td>
<td>无连接</td>
</tr>
<tr>
<td>可靠性</td>
<td>可靠、有序、不重复</td>
<td>尽最大努力交付，可能丢包乱序</td>
</tr>
<tr>
<td>数据形式</td>
<td>字节流，无消息边界</td>
<td>数据报，有消息边界</td>
</tr>
<tr>
<td>控制能力</td>
<td>有流量控制、拥塞控制</td>
<td>无内置流控和拥塞控制</td>
</tr>
<tr>
<td>头部开销</td>
<td>至少 20 字节</td>
<td>固定 8 字节</td>
</tr>
<tr>
<td>适合场景</td>
<td>文件传输、网页、数据库连接</td>
<td>DNS、音视频、游戏、QUIC</td>
</tr>
	</table>
</details>
<details>
<summary>TCP 为什么可靠</summary>
	TCP 可靠性来自多个机制共同作用：
	- 连接管理：三次握手建立连接，四次挥手释放连接。
	- 序列号：每个字节都有序号，用于排序、去重和重传。
	- 确认应答：接收方通过 ACK 告诉发送方哪些数据已收到。
	- 超时重传：超过 RTO 未收到 ACK 就重传。
	- 快重传：收到 3 个重复 ACK 时，不等超时就重传可能丢失的包。
	- 校验和：检测传输过程中的比特错误。
	- 流量控制：通过接收窗口避免把接收方缓冲区打满。
	- 拥塞控制：通过拥塞窗口避免把网络打崩。
</details>
<details>
<summary>TCP 粘包是什么，怎么解决</summary>
	TCP 是字节流协议，没有消息边界。发送方多次写入的数据，接收方可能一次读到；发送方一次写入的数据，接收方也可能分多次读到，这就是常说的粘包/拆包问题。
	解决方式本质上是定义应用层消息边界：
	- 固定长度：每个消息固定 N 字节。
	- 分隔符：用特殊字符标识消息结束，例如换行。
	- 长度字段：自定义协议头，先读长度，再按长度读 body。
	实际项目里最常用的是“长度字段 + 消息体”。
</details>
<details>
<summary>怎么用 UDP 实现 HTTP</summary>
	HTTP/3 就是基于 UDP 的 QUIC 实现的。
	UDP 本身不可靠，所以 QUIC 在用户态实现了类似 TCP 的能力：
	- 可靠传输：包编号、确认、重传。
	- 拥塞控制：根据网络状态调整发送速度。
	- 多路复用：多个 Stream 独立传输，减少队头阻塞。
	- TLS 1.3 内置：握手更快，安全性更好。
	- 连接迁移：通过 Connection ID 识别连接，IP 或网络切换后仍可保持连接。
</details>
# 网络场景
<details>
<summary>从输入 URL 到页面展示发生了什么</summary>
	以访问 HTTPS 网站为例：
	1. URL 解析：浏览器解析协议、域名、端口、路径和参数。
	2. 缓存检查：检查浏览器缓存、系统缓存、hosts、本地 DNS 缓存等。
	3. DNS 解析：把域名解析成 IP。
	4. 获取下一跳 MAC：通过子网判断目标是否在同一网段；同网段 ARP 获取目标 MAC，不同网段 ARP 获取网关 MAC。
	5. TCP 三次握手：和目标服务器建立 TCP 连接。
	6. TLS 握手：校验证书、协商密钥，建立 HTTPS 加密通道。
	7. 发送 HTTP 请求：浏览器发送请求行、请求头和可选请求体。
	8. 服务端处理：经过负载均衡、网关、应用服务、数据库或缓存后生成响应。
	9. 返回 HTTP 响应：浏览器接收 HTML、CSS、JS、图片等资源。
	10. 页面渲染：解析 HTML 构建 DOM，解析 CSS 构建 CSSOM，执行 JS，布局、绘制、合成，最终展示页面。
</details>
<details>
<summary>网页一直转圈，如何定位问题</summary>
	可以按链路从客户端到服务端排查：
	1. 客户端环境：能否访问其他网站，网络、代理、VPN、DNS 配置是否正常。
	2. DNS：域名是否解析成功，解析出的 IP 是否正确。
	3. 连通性：能否建立 TCP 连接，端口是否开放，防火墙或安全组是否拦截。
	4. TLS：证书是否过期、域名是否匹配、TLS 握手是否失败。
	5. HTTP：请求是否发出，响应状态码是多少，是否卡在 TTFB 或下载阶段。
	6. 服务端：查看 Nginx、网关、应用日志，确认是否超时、报错、线程池打满、数据库慢查询。
	7. 网络质量：抓包看是否丢包、重传、窗口过小、RTT 过高。
	工具上可以用浏览器 Network 面板、`curl -v`、`ping`、`telnet/nc`、`traceroute`、抓包和服务端日志配合定位。
</details>
