# 前言
今天我们继续啃信息论之父香农发布的论文A Mathematical Theory of Communication(通信中的数学理论)

![请添加图片描述](https://img-blog.csdnimg.cn/dfdbe2756c4a4d9a898c0d7575dfc770.jpeg)


# 离散信道
离散信道的容量`C`的定义如下:
![在这里插入图片描述](https://img-blog.csdnimg.cn/02d88eb25dcc418b95359c37ea1a8188.png)
`N(T)`表示时间为`T`的信号数目

如果出现信号 S1,...,Sn  的所有序列，这些符号的持续时间为 t1, ...,tn 。那么如何计算信道容量?

首先当然是计算S1,...,Sn  的所有序列数的和, 也就是`N(t)`![在这里插入图片描述](https://img-blog.csdnimg.cn/f17f4907dc4845fca0cbdda3c003768e.png)

N(t) is then asymptotic for large t to Xt0 where X0 is the largest real solution of the characteristic equation, 这里奇妙地给出了一个特征方程, 大佬并没有给出证明。。。于是最大的N(t) -> Xt0， 我们可以解出该方程最大实数解X0:
![在这里插入图片描述](https://img-blog.csdnimg.cn/71c58c873538477c94acffa81b03d5a6.png)
至于这是怎么推导的呢? 首先我们要知道差分方程的特征方程的求法规律:
假设我们存在一个差分方程`Y(x + 1) - aY(x) = 0`
假设`Y(0)`已知, 我们如何解这个方程呢? 下面给出过程:
`Y(1) = aY(0)`
`Y(2) = a*a*Y(0)`
`Y(3) = a*a*a*Y(0)`
...
`Y(X) = a ^x * Y(0)`
令Y(0) = C
于是差分方程的通解为`Y(X) = C*a^x`
因此差分方程的解是一种指数形式， 于是我们就可以得出上式了:
![在这里插入图片描述](https://img-blog.csdnimg.cn/9774901dc9624cb59d64096e37628e8b.jpeg#pic_center)


因此根据离散信道的容量`C`的定义可化简为:
![在这里插入图片描述](https://img-blog.csdnimg.cn/d346a9f79a2c4ea3b6895f0ccc8275de.png)

# 离散信源
在电报通信中，要传送的消息由字符序列组成。而这些字符序列中的字符出现的频率是不一样的, 就像E的出现频率要高于Q。我们就可以通过一些特殊方法进行处理来节省通信容量和时间。

何为离散? 就是一堆不连续的变量，在我看来更像是一种随机过程，正如香农所说:
Conversely, any stochastic process which produces a discrete sequence of symbols chosen from a finite set may be considered a discrete source.
离散符号序列是从有限集合中选出的随机变量, 就是离散信源.

接下来香农开始给我们展示了几种案例的马尔科夫过程, 这里就不记录啦!  
![在这里插入图片描述](https://img-blog.csdnimg.cn/5c36c63df802454182104e60378090e0.png)


# 信息熵的定义
因此, 由于离散信源是随机的过程, 我们能不能定义一个量，度量这样一个过程“生成”多少信息？甚至度量它以什么样的速率生成信息？

于是就定义了信息熵H(p1, p2, ..., pN), 并能够满足一下三条假定:
* H 关于 Pi 连续
* 如果所有Pi相等, 则Pi = 1 / n
* 如果一项选择被分解为两个连续选择，则原来的 H 应当是各个 H 值的加权和:  
![在这里插入图片描述](https://img-blog.csdnimg.cn/cee2e424ffd148e2a7de2b43ebd943e0.png)

以下一图直观地表示了这一等价关系:  
![在这里插入图片描述](https://img-blog.csdnimg.cn/fcc0b104205f41cd9727f8cd8dae8528.png)


那么
满足以上假定的`H`就可以这样定义:  
![在这里插入图片描述](https://img-blog.csdnimg.cn/27f9ef1d2be045968b9e3916a653d532.png)
假设存在随机变量`X`, 我们将H(X)记为它的熵.
