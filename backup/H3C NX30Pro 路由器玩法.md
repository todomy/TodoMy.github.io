> [!TIP]
> H3C NX30Pro厂家默认开启telnet端口，让这百元wifi6路由器通过刷写系统装插件等，让其拥有非凡能力，可玩性极高。

## 硬件介绍
H3C NX30Pro是一款面向家用市场的高性能Wi-Fi 6路由器，以下是其硬件介绍：



### 外观设计
- **立式造型**：采用类“信号塔”全新立式造型，搭配5根外置高增益天线，机身采用“Ⅰ”型设计，降低信号衰减的可能，使得信号场强更饱满。
- **散热设计**：背部镂空，搭配定制散热片，整体散热效果增强20%，运行更稳更流畅。

### 无线性能
- **速率**：整机并发速率高达3000Mbps，其中5GHz无线速率是AX1800路由器无线速率的2倍。
- **频宽**：5GHz支持160MHz超大频宽，信道速度提升近1倍，同时兼容20M/40M/80MHz频宽接入。
- **传输技术**：采用Wi-Fi 6核心技术OFDMA，最多支持一次传输为8个终端设备发送上下行数据，网络延迟降低36%。

### 网络接口
- **千兆网口**：提供1个1000M WAN口和3个1000M LAN口。
- **Mesh组网**：支持EasyMesh组网，适应多种户型，全屋Wi-Fi覆盖，自由活动，不怕掉线。

### 芯片与内存
- **处理器**：采用联发科MT7981B芯片，双核ARM A53架构，频率1.3GHz。
- **内存与存储**：配备256MB DDR3内存和128MB Flash。

### 天线与信号
- **天线配置**：5根外置全向天线，其中2根用于2.4G频段，3根用于5G频段。
- **信号放大器**：内置五颗信号放大器，增强覆盖性能，弥补远距离传输缺陷。

## 刷入Easywrt系统
### 开启 SSH
这一步请确保路由器能正常联网。NX30 Pro 默认开启了 telnet，默认的地址是 192.168.124.1，用户名是 H3C（全大写），密码就你设置的路由器后台密码，端口是 99。
打开[ termius](https://termius.com/)选择 New Host 添加，Address 填写 192.168.124.1，取消勾选 SSH，勾选 Telnet，Port 端口填写上 99。然后输入用户名和密码，输入密码不会显示，回车即可连上 Telnet。



然后复制下面的代码到终端里执行即可开启 SSH：
```
curl -o /tmp/dropbear.ipk https://downloads.openwrt.org/releases/packages-19.07/aarch64_cortex-a53/base/dropbear_2019.78-2_aarch64_cortex-a53.ipk
opkg install /tmp/dropbear.ipk
/etc/init.d/dropbear enable
/etc/init.d/dropbear start
```


### 刷写 uboot
然后打开 WinSCP，文件协议选择 SCP，主机名 192.168.124.1，端口号 22，用户名 H3C，然后登录输入密码就能连上。登录后，将下载好的 uboot.bin 文件从左边电脑拖进右侧路由器 tmp 路径下。然后执行命令，如图所示完成了写入 uboot。（也可以直接用 [FinalShell](https://www.hostbuf.com/t/988.html)上传文件和执行命令）
```
cd /tmp
md5sum uboot.bin
mtd write /tmp/uboot.bin FIP
```


###  刷写Easywrt
路由器断电后，先按住背后 Reset 恢复按钮不放，再插电，等待 10s 左右松开背后 Reset，路由器就进入了 uboot，电脑用网线连接路由器 LAN1，并设置好静态 IP：IP地址填 192.168.1.2，子网掩码 255.255.255.0，网关 192.168.1.1，DNS 192.168.1.1。现在浏览器打开  192.168.1.1 就能打开 uboot 后台。然后上传Easywrt升级包，然后点击升级，update；趁空将电脑IP设置为自动获取，取消刚刚设置的静态IP。

##  安装OpenClash插件
###  下载上传插件
```
固件管理ip：192.168.2.1
用户名：root
密码：无密码
```
登录路由器管理后台，到GitHub上下载所需要的插件[链接](https://github.com/AUK9527/Are-u-ok/tree/main/apps)，下载完后，上传安装。

![Image](https://github.com/user-attachments/assets/ad00076c-783c-4f1b-b414-8691c36521c2)
如果提示安装失败，或者缺少依赖，可以更换镜像源，以修改/etc/opkg/distfeeds.conf 文件，修改镜像源，也可以在系统后台里进行修改配置。

![Image](https://github.com/user-attachments/assets/20345a63-3e05-4bc1-8217-d13d137d34e6)

###  配置OpenClash
配置订阅

![Image](https://github.com/user-attachments/assets/61e1eefc-4ce3-422c-af4d-99d54f0200d1)

 插件配置

![Image](https://github.com/user-attachments/assets/335672c4-84be-49e9-b04b-97104980d929)

 启动

![Image](https://github.com/user-attachments/assets/9f27d5fa-901a-40f6-878c-2852cf140a32)

其他个性化黑白名单规则等根据自身需求自行设置，日常管理通过Yacd控制面板进行节点选择

![Image](https://github.com/user-attachments/assets/3c2c21ce-426b-43c4-ac95-adbbf72d6a7e)

##  网络加速
系统内置了网络加速组件，支持快速转发引擎 MediaTek HNAT，全锥形 NAT，TCP 拥塞控制算法，按需选择开启有效提高网速和稳定性。

![Image](https://github.com/user-attachments/assets/b477897f-9623-4414-ab4c-a37b7d973c81)

##  附件
[软件包](https://github.com/todomy/TodoMy.github.io/tree/main/%E9%99%84%E4%BB%B6/H3C%20NX30Pro)