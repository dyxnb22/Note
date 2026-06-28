# Note

**DDD 四层架构**

1. trigger 层（触发器层）接收 HTTP / MQ / Job / RPC，校验、鉴权、转发

<table header-row="true">
<tr>
<td>**子包**</td>
<td>**职责**</td>
<td>**典型类**</td>
</tr>
<tr>
<td>`http/`</td>
<td>REST API 入口</td>
<td>`RaffleActivityController`、`RaffleStrategyController`、`ErpOperateController`、`DCCController`</td>
</tr>
<tr>
<td>`listener/`</td>
<td>RabbitMQ 消费者</td>
<td>`SendAwardConsumer`、`RebateMessageConsumer`、`CreditAdjustSuccessConsumer`、`ActivitySkuStockZeroConsumer`</td>
</tr>
<tr>
<td>`job/`</td>
<td>XXL-Job 定时任务</td>
<td>`SendMessageTaskJob`、`UpdateAwardStockJob`、`UpdateActivitySkuStockJob`</td>
</tr>
<tr>
<td>`rpc/`</td>
<td>Dubbo RPC 提供方</td>
<td>`RebateServiceRPC`、`RaffleStrategyServiceRPC`</td>
</tr>
<tr>
<td>`adapter/`</td>
<td>跨服务调用的适配边界</td>
<td>`IStrategyReadAdapter`、`IAwardDispatchAdapter`、`IAccountCreditWriteAdapter` 等</td>
</tr>
</table>

1. application 层（应用层）编排领域服务，串联一次完整业务流程
2. domain 层（领域层）— 核心业务规则、聚合、实体、值对象、领域服务
3. infrastructure 层（基础设施层）实现 repository / port，对接 DB、Redis、MQ 等
