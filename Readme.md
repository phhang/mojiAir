# 墨迹天气空气果2 HomeAssistant 集成

（在下就是当年原价买这个产品的大怨种一枚，最近想起来了才打算接入HA）

![空气果2](https://y.zdmimg.com/201802/08/5a7bfc67b9a302365.jpg_d320.jpg)

基本参考[此帖](https://bbs.hassbian.com/thread-3812-1-1.html), 仍需墨迹的服务器。以后等服务器真挂了再考虑DNS劫持+离线版的。

## 请求流程抓包

Charles或者Fiddler等HTTP代理均可。部分请求是HTTP without SSL所以甚至不安装证书也行

主要流程是两部分：

1. 触发检测

发POST到`http://has.moji001.com/HAS/DetectedImmediately`

Content type是`application/x-www-form-urlencoded`

Parameter只需要这些即可： station-id, sns-id, identifier, session-id, machine-id

Response长这样：
```json
{"id":66666,"rc":{"c":0,"p":"操作成功"},"ts":1692505695172}
```

2. 读取结果

还是POST：`http://has.moji001.com/HAS/PersonPage`

Parameter只需要session-id以及sns-id

结果如下：
```json
{
  "rc": {
    "c": 0,
    "p": "操作成功"
  },
  "result": [
    {
      "battery": "100",
      "charge": 0,
      "cityId": 666,
      "datas": {
        "detectTime": 1692488898000,
        "hcho": 0.0,
        "hchoDesc": "优",
        "hchoLevel": 0,
        "humidity": 54.2,
        "humidityDesc": "舒适",
        "humidityLevel": 0,
        "pm25": 6.0,
        "pm25Desc": "优",
        "pm25Level": 0,
        "pressure": 0,
        "pressureDesc": "",
        "pressureLevel": 0,
        "temp": 26.43,
        "tempDesc": "偏暖",
        "tempLevel": 0
      },
      "hardwareType": 5,
      "id": 66666,
      "isBind": true,
      "isOffLine": 0,
      "location": "某某市",
      "mac": "DEADBEEF2333",
      "name": "TA的空气果2",
      "prompts": [
        {
          "desc": "较适宜给婴儿洗澡",
          "tips": "室内温度较高，婴儿洗澡容易感觉憋闷，建议打开新风换气，并避免婴儿处于风口下方。"
        }
      ],
      "visible": 2
    }
  ]
}
```

其中detectTime是Unix timestamps in milliseconds，甲醛单位是mg/m3

## HomeAssistant 怎么用

对于触发检测，HA自带的[Restful command](https://www.home-assistant.io/integrations/rest_command/)较为好用，也能集成在automation中方便定时触发。对应`configuration.yaml`如下：

```yaml
rest_command:
  airnut_refresh:
    url: 'http://has.moji001.com/HAS/DetectedImmediately?params...'
    method: post
```

读取结果可参考此repo中的`sensor.py`. 用法是在`configuration.yaml`同目录下建立文件夹`custom_components`, 将`mojiAir`文件夹放入其中。一开始HA总是找不到integration，直到后来发现问题是`manifest.json`里面少了版本号…

对应`configuration.yaml`如下。记得用check configuration检查之后再restart

```yaml
sensor:
  - platform: mojiAir
    moji_url: 'http://has.moji001.com/HAS/PersonPage?params...'
    scan_interval: 3600
```

## 其他

当初感觉空气果这个产品还是挺有情怀的，但是仅仅有检测功能而无法和空气净化器集成就让这款产品的价值大打折扣。也罢，毕竟中国互联网只有做超级App卷死其他对手一条出路。还有恭喜低价买到这批空气果的垃圾佬们成功的避开了资本主义的消费陷阱


