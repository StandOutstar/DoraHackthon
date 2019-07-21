# CommentChain Demo Project For DoraHackthon NEO

## 项目愿景
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Comment chain 是一个基于区块链技术来记录商品真实评论的产品。Comment chain共包括两条链，一条是评论链，用于记录商品的用户评论，区块链的特性能够保证所有的用户评论能够被真实地记录下来；另一方面，为了识别出恶意评论等刷单行为，我们特地构建了「支付链」，支付链能够精准的记录链条上的支付行为，当有象征着刷单的支付行为出现时，就能够直接将其识别出来。

## 运行方式
```shell
$ flask init-db  // 初始化数据，再次可不用执行
$ export FLASK_APP=CommentChain  // 设置环境变量
$ export FLASK_ENV=development  // 设置环境变量
$ flask run  // 运行
```