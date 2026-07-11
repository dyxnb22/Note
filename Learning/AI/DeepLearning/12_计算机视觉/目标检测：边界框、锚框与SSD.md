# 目标检测：边界框、锚框与 SSD

分类回答“是什么”，检测还要回答“在哪里”。边界框常用 `(xmin,ymin,xmax,ymax)` 或中心点宽高表示；IoU 衡量预测框与真框重叠。检测损失通常结合分类损失和定位损失。

锚框在不同位置/尺度预设候选框，训练时按 IoU 匹配真框；SSD 在多个特征尺度预测类别和偏移，速度快但小物体较难。NMS 删除高度重叠的重复框；阈值选择会影响 precision/recall。

`#object-detection #iou #ssd #nms`
