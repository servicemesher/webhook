# Istio 官网翻译 webhook

用于 https://github.com/servicemesher/istio-official-translation/issues 中回复关键词触发。

所有指令，都在 Issue 中以 Comment 的形式输入，仅对 Member 有效。如果出错或者不符合条件，不会有任何提示。

1. `/accept`: 适用于 `pending` 状态，且当前无人指派的 Issue，输入该指令，会将该 Issue 指派给当前用户。并变更状态为 `translating`
1. `/pushed`: 适用于 `translating` 状态的 Issue，输入该指令，会将该 Issue 指派给当前用户。并变更状态为 `pushed`
1. `/merged`: 适用于 `pushed` 状态的 Issue，输入该指令，会将该 Issue 指派给当前用户。并变更状态为 `finished`，然后关闭 Issue