# 宀愰粍灏忕瓚 路 鍔熻兘鏂囨。

> 涓尰鍏荤敓绉戞櫘涓撻绔?路 7 璇 路 Jekyll 闈欐€佺珯
>
> README 璁查儴缃诧紝鏈枃璁层€屽畠鑳藉仛浠€涔堛€嶄笌銆屾€庝箞鎵╁睍銆嶃€?
## 鐩綍

1. [绔欑偣姒傝](#1-绔欑偣姒傝)
2. [URL 璺敱](#2-url-璺敱)
3. [椤甸潰浣撶郴](#3-椤甸潰浣撶郴)
4. [鍐呭绠＄悊](#4-鍐呭绠＄悊)
5. [澶氳瑷€ (i18n)](#5-澶氳瑷€-i18n)
6. [甯冨眬涓庣粍浠禲(#6-甯冨眬涓庣粍浠?
7. [鎼滅储](#7-鎼滅储)
8. [涓婚](#8-涓婚)
9. [閮ㄧ讲 CI/CD](#9-閮ㄧ讲-cicd)
10. [鏈湴寮€鍙慮(#10-鏈湴寮€鍙?
11. [甯哥敤鎿嶄綔](#11-甯哥敤鎿嶄綔)
12. [鏁呴殰鎺掓煡](#12-鏁呴殰鎺掓煡)
13. [椤圭洰缁撴瀯閫熸煡](#13-椤圭洰缁撴瀯閫熸煡)

---

## 1. 绔欑偣姒傝

**宀愰粍灏忕瓚** 鈥斺€?涓€鍗枫€婂唴缁忋€嬨€佸崐鐩忔竻鑼剁殑涓尰鍏荤敓绉戞櫘绔欍€?
| 缁村害 | 瑙勬牸 |
| --- | --- |
| 寮曟搸 | Jekyll 4 + GitHub Pages 闈欐€佹瀯寤?|
| 閮ㄧ讲 | push `main` 鈫?GitHub Actions 鈫?鎺ㄩ€?`_site` |
| 婧愬湴鍧€ | https://xiebingcheng.github.io/-shiyan-/ |
| 璇 | 7 绉嶏細zh-CN锛堥粯璁わ級 / en / ru / fr / es / id / ar |
| 鍐呭 | 15 绡囩ず渚嬫枃绔?脳 7 璇 = 105 绡囷紱6 澶у垎绫伙紱55 涓爣绛?|
| 涓婚 | 鍙ら锛堝绾?/ 澧?/ 鏈辩孩 / 榛涢潚锛屾シ浣?+ 瀹嬩綋锛夛紝鏄?鏆楀弻涓婚 |
| 鎼滅储 | 瀹㈡埛绔?substring + 澶氬叧閿瘝 AND锛屽姞鏉冭瘎鍒?+ 鍛戒腑楂樹寒 |
| 閫傞厤 | 妗岄潰 / 骞虫澘 / 鎵嬫満锛涢敭鐩樺鑸?/ ARIA / 璺冲埌姝ｆ枃 |

---

## 2. URL 璺敱

### 2.1 鍩虹璺緞

`_config.yml` 涓細

```yaml
url: "https://xiebingcheng.github.io"
baseurl: "/-shiyan-"
```

### 2.2 璇鍓嶇紑

| 璇 | 鍓嶇紑 | 渚嬪瓙 |
| --- | --- | --- |
| zh-CN锛堥粯璁わ級 | 鏃?| `/archive/` |
| en | `/en/` | `/en/archive/` |
| ru | `/ru/` | `/ru/archive/` |
| fr | `/fr/` | `/fr/archive/` |
| es | `/es/` | `/es/archive/` |
| id | `/id/` | `/id/archive/` |
| ar | `/ar/` | `/ar/archive/` |

### 2.3 瀹屾暣 URL 绀轰緥

```
/                              鈫?zh-CN 棣栭〉
/en/                           鈫?鑻辨枃棣栭〉
/ar/2026/10/08/hanlu-yanfei/   鈫?闃挎媺浼銆屽瘨闇层€?/categories/jieqi/             鈫?涓枃 鑺傛皵鍏荤敓 鍒嗙被
/en/categories/jieqi/          鈫?鑻辨枃 Solar Terms锛堥渶缈昏瘧鐗堝瓨鍦級
/tags/鑺傛皵/                      鈫?銆岃妭姘斻€嶆爣绛鹃〉锛堜腑鏂?tag 鑷姩 URL 缂栫爜锛?/en/tags/                      鈫?鑻辨枃鏍囩浜?/search/                       鈫?鎼滅储椤?/about/                        鈫?鍏充簬灏忕瓚
/about-zhongyi/                鈫?浠€涔堟槸涓尰
/feed.xml                      鈫?RSS
/sitemap.xml                   鈫?sitemap
```

---

## 3. 椤甸潰浣撶郴

### 3.1 椤跺眰椤甸潰

| 椤甸潰 | 婧愭枃浠?| 鐢ㄩ€?|
| --- | --- | --- |
| 棣栭〉 | `index.html`锛坺h锛? `<lang>/index.md` 脳 6 | 鍚勮绉嶆渶鏂?10 绡?|
| 褰掓。 | `archive.md`锛坺h锛? 6 涓炕璇戠増 | 鎸夊勾/鏈堢殑鏂囩珷鍒楄〃 |
| 鍒嗙被鎬昏 | `categories.md`锛坺h锛? 6 涓炕璇戠増 | 6 绫诲叆鍙?+ 姣忕被鍓?10 绡?|
| 鍗曞垎绫?| `categories/<slug>.md`锛? 涓級 | 鍗曞垎绫讳笅鎵€鏈夋枃绔狅紙浠?zh锛岃剼鏈敓鎴愶級 |
| 鏍囩鎬昏 | `tags.md`锛坺h锛? 6 涓炕璇戠増 | 鏍囩浜?|
| 鍗曟爣绛?| `tags/<tag>.md`锛?5 涓級 | 鍗曟爣绛句笅鎵€鏈夋枃绔狅紙浠?zh锛岃剼鏈敓鎴愶級 |
| 鎼滅储 | `search.md`锛坺h锛? 6 涓炕璇戠増 | 瀹㈡埛绔悳绱㈢晫闈?|
| 鍏充簬 | `about.md`锛坺h锛? 6 涓炕璇戠増 | 鍏充簬灏忕瓚 |
| 浠€涔堟槸涓尰 | `about-zhongyi.md`锛坺h锛? 6 涓炕璇戠増 | 涓尰绉戞櫘 |

### 3.2 鏂囩珷璇︽儏

鐢?`post.html` 甯冨眬娓叉煋锛?
- 鍒嗙被寰界珷锛堝甫棰滆壊 + 鍥炬爣锛?- 鏍囬 + 鍓爣棰?- 鍙戝竷鏃ユ湡 / 鍒嗙被 / 鏍囩 / 闃呰鏃堕暱
- 姝ｆ枃
- **鍚岃绉?*銆屼笂涓€绡?/ 涓嬩竴绡囥€嶅鑸紙鎸夊綋鍓嶈绉嶈繃婊ゅ悗鐨勭浉閭绘枃绔狅級
- 鏍囩 chips
- 銆屽洖鍒伴椤点€嶆寜閽?
---

## 4. 鍐呭绠＄悊

### 4.1 鏂囩珷锛坄_posts/`锛?
鏂囦欢鍚嶈鑼冿細`YYYY-MM-DD-slug.md`锛坰lug 鐢ㄨ嫳鏂?鎷奸煶 + 杩炲瓧绗︼級銆?
front matter 瀛楁锛?
```yaml
---
layout: post
title: "瀵掗湶锛氱娣遍湶閲嶏紝娑﹁偤鍏婚槾"
subtitle: "銆屼節鏈堣妭锛岄湶姘斿瘨鍐凤紝灏嗗嚌缁撲篃銆?      # 鍙€?date: 2026-10-08 08:30:00 +0800
author: 宀愰粍灏忕瓚
category: jieqi                              # 6 閫?1锛歫ieqi / shiliao / siji / jingluo / qiju / qingzhi
tags: [瀵掗湶, 鑺傛皵, 娑﹁偤, 鍏婚槾, 绉嬪]
excerpt: 瀵掗湶鏃惰妭锛岄湶姘村甫瀵掞紝绉嬫剰娓愭祿銆?       # 鐢ㄤ簬鍗＄墖 / 鎼滅储鎽樿
lang: zh-CN                                  # 鈫?鍏抽敭锛氬璇杩囨护
permalink: /2026/10/08/hanlu-yanfei/         # 缈昏瘧鐗堥渶甯﹁绉嶅墠缂€
dir: rtl                                     # 浠?ar 璇
---
```

> **鍏抽敭锛歚lang` 瀛楁**
>
> 鎵€鏈夊垪琛?layout 鐢?`where: 'lang', cur_lang` 杩囨护褰撳墠璇鏂囩珷銆傛簮鏂囩珷锛堜腑鏂囷級**蹇呴』鏄惧紡鍐?`lang: zh-CN`**锛屽洜涓?Jekyll 鐨?`defaults` 鍦?GitHub Pages 闀滃儚涓婂 `posts` 闆嗗悎涓嶅彲闈犮€傜炕璇戠増鍦?`<lang>/_posts/` 瀛愮洰褰曪紝permalink 涔熷甫鍓嶇紑锛屽 `/en/2026/02/04/lichun-yangsheng/`銆?
### 4.2 椤跺眰椤甸潰

`about.md` / `archive.md` / `categories.md` / `tags.md` / `search.md` / `index.html` 鍦ㄤ粨搴撴牴锛岀炕璇戠増鍦?`<lang>/` 瀛愮洰褰曘€?
### 4.3 鍒嗙被涓庢爣绛?
| 鏁版嵁 | 浣嶇疆 |
| --- | --- |
| 鍒嗙被鍏冩暟鎹紙slug / name / desc / color / icon锛?| `_data/categories.yml` |
| 鍒嗙被 7 璇鍚嶇О + 鎻忚堪 | `_data/categories-i18n.yml` |
| 鏍囩鑱氬悎 | 鏉ヨ嚜姣忕瘒鏂囩珷 front matter 鐨?`tags:` 瀛楁 |
| 鍗曚釜鍒嗙被椤?/ 鍗曚釜鏍囩椤?| `tools/generate_archives.py` 鑷姩鐢熸垚 |

璺戞硶锛?
```bash
python tools/generate_archives.py
```

> 璇ヨ剼鏈粎鎵?`_posts/`锛堟簮鏂囩珷 zh-CN锛夈€傚鏋滈渶瑕佺炕璇戠増鍒嗙被/鏍囩椤碉紙濡?`/en/categories/jieqi/`锛夛紝闇€鎵嬪姩寤恒€?
---

## 5. 澶氳瑷€锛坕18n锛?
### 5.1 璇鏀寔

| 浠ｇ爜 | 璇 | RTL | 瑙掕壊 |
| --- | --- | :-: | --- |
| zh-CN | 绠€浣撲腑鏂?| 鉁?| 婧愯瑷€ |
| en | English | 鉁?| 缈昏瘧 |
| ru | 袪褍褋褋泻懈泄 | 鉁?| 缈昏瘧 |
| fr | Fran莽ais | 鉁?| 缈昏瘧 |
| es | Espa帽ol | 鉁?| 缈昏瘧 |
| id | Bahasa Indonesia | 鉁?| 缈昏瘧 |
| ar | 丕賱毓乇亘賷丞 | 鉁?| 缈昏瘧 + RTL |

### 5.2 URL 瑙勫垯

- zh-CN 鏃犲墠缂€锛歚/`, `/archive/`, `/categories/jieqi/`
- 鍏朵粬 6 璇缁熶竴鍔?`/<code>/` 鍓嶇紑
- 椤堕儴瀵艰埅銆乫ooter 閾炬帴鐢?Liquid 鏉′欢 `if cur_lang == 'zh-CN'` 鍐冲畾鏄惁鍔犲墠缂€

### 5.3 UI 瀛楃涓?
| 鏂囦欢 | 鍐呭 |
| --- | --- |
| `_data/i18n.yml` | 璇鍏冧俊鎭紙`langs`锛? 7 璇鐣岄潰鏂囨锛坄strings.<code>`锛?|
| `_data/nav-i18n.yml` | 椤堕儴瀵艰埅 7 璇鏍囬 |
| `_data/categories-i18n.yml` | 鍒嗙被 7 璇 name + desc |

### 5.4 鏂囩珷姝ｆ枃缈昏瘧

姣忕瘒婧愭枃绔犲搴?6 涓炕璇戠増锛堝悓鍚嶆枃浠躲€佷笉鍚屽瓙鐩綍锛夛細

```
_posts/2026-02-04-lichun-yangsheng.md         鈫?zh-CN 婧?en/_posts/2026-02-04-lichun-yangsheng.md       鈫?en
ar/_posts/2026-02-04-lichun-yangsheng.md       鈫?ar
...
```

缈昏瘧瑙勮寖锛?
- front matter 蹇呴』鍚?`lang: <code>` 鍜?`permalink: /<code>/YYYY/MM/DD/<slug>/`
- 浠?`ar` 鍔?`dir: rtl`
- 鏈鏍煎紡锛歚<native>锛堟眽瀛? p墨ny墨n, English锛塦锛屼緥濡?`H谩nl霉锛堝瘨闇? H谩nl霉, Cold Dew锛塦
- 鏂囨湯淇濈暀 `<!-- Translated by translation-specialist agent -->`

### 5.5 瀹㈡埛绔垏鎹?
`assets/js/i18n.js`锛?
1. 璇?URL 绗竴娈?`/<xx>/` 鍐冲畾褰撳墠璇
2. 涔熸敮鎸?`?lang=xx` 涓?`localStorage` 璁板繂
3. 鍒囨崲鏃?*鍏堝墺 `baseurl` 鍐嶆嫾鐩爣鍓嶇紑**锛岄伩鍏?`/en/-shiyan-/...` 杩欑 404
4. `ar` 鑷姩缁?`<html dir="rtl" lang="ar">`
5. 榛樿璇鐢?`_config.yml` 鐨?`default_lang: zh-CN` 鎺у埗

### 5.6 鍒楄〃鎸夎绉嶈繃婊?
`home` / `archive` / `category` / `tag` / `categories` / `tags` 鍏釜 layout 浠ュ強 `post.html` 鐨勪笂涓€绡?涓嬩竴绡囷紝閮界敤鍚屼竴涓ā寮忥細

```liquid
{%- assign cur_lang = page.lang | default: site.default_lang -%}
{%- assign lang_posts = site.posts | where: 'lang', cur_lang -%}
```

> 鈿狅笍 **涓嶈**鐢?`where_exp: "p.lang == empty or ..."` 鍏滃簳 鈥斺€?Jekyll `where_exp` 瀵?`empty` 鍏抽敭瀛楄涓轰笉绋冲畾锛屽疄娴嬩細涓?14/15 绡囥€?
---

## 6. 甯冨眬涓庣粍浠?
### 6.1 甯冨眬锛坄_layouts/`锛?
| 鏂囦欢 | 鐢ㄩ€?|
| --- | --- |
| `default.html` | 鍏ㄥ眬妗嗘灦锛坄<html>` + `header` + `main` + `footer`锛夛紝鍚?RTL 鍒囨崲 |
| `home.html` | 棣栭〉锛坔ero + 鏈€鏂?10 绡?+ 6 澶у垎绫诲叆鍙ｏ級 |
| `post.html` | 鏂囩珷璇︽儏锛堝悓璇涓婁竴绡?涓嬩竴绡囷級 |
| `page.html` | 閫氱敤椤甸潰锛堝叧浜庛€佸綊妗ｃ€佹悳绱㈢瓑锛?|
| `archive.html` | 褰掓。锛堟寜骞村垎缁勶級 |
| `categories.html` | 鍒嗙被鎬昏锛? 绫诲悇鍒楀墠 10 绡囷級 |
| `category.html` | 鍗曞垎绫婚〉 |
| `tags.html` | 鏍囩浜戯紙鎸夊綋鍓嶈绉嶈繃婊わ級 |
| `tag.html` | 鍗曟爣绛鹃〉 |
| `search.html` | 鎼滅储椤碉紙绾墠绔級 |
| `404.html` | 404 |

### 6.2 缁勪欢锛坄_includes/`锛?
| 鏂囦欢 | 鐢ㄩ€?|
| --- | --- |
| `head.html` | `<head>`銆丆SS 寮曞叆銆侀槻闂儊 inline 涓婚鑴氭湰 |
| `header.html` | 椤堕儴瀵艰埅 + 璇█鍒囨崲鍣?+ 涓婚鍒囨崲 |
| `footer.html` | 椤佃剼锛堢珯鐐逛俊鎭€侀摼鎺ャ€佺増鏉冿級 |
| `lang-switcher.html` | 7 璇涓嬫媺鍒囨崲鍣?|
| `post-card.html` | 鏂囩珷鍗＄墖锛堥椤?/ 鍒楄〃澶嶇敤锛?|
| `post-meta.html` | 鏂囩珷鍏冧俊鎭紙鏃ユ湡 / 鍒嗙被 / 鏍囩 / 瀛楁暟 / 闃呰鏃堕暱锛?|
| `pagination.html` | 鍒嗛〉瀵艰埅锛堝綋鍓?home 宸插純鐢紝璇﹁ 搂 12.2锛?|

### 6.3 璧勬簮锛坄assets/`锛?
| 鏂囦欢 | 鐢ㄩ€?|
| --- | --- |
| `css/main.css` | 涓绘牱寮忥紙鍙ら + 鍝嶅簲寮?+ 鏆楄壊锛?|
| `js/theme.js` | 鏄?鏆椾富棰樺垏鎹紙localStorage锛?|
| `js/nav.js` | 绉诲姩绔眽鍫¤彍鍗?|
| `js/i18n.js` | 瀹㈡埛绔瑷€鍒囨崲 |
| `js/search.js` | 瀹㈡埛绔悳绱?|
| `img/*.svg` | Logo / 鍗扮珷 / 鑺傛皵鍥炬爣 |

---

## 7. 鎼滅储

### 7.1 瀹炵幇

- **绾鎴风**锛屼笉渚濊禆 lunr.js
- 涓枃鐢?`String.indexOf` 鍋?substring 鍖归厤
- 澶氬叧閿瘝鏀寔 AND 缁勫悎
- 璇勫垎锛?*鏍囬 4 / 鏍囩 3 / 鍒嗙被 3 / 鎽樿 2 / 姝ｆ枃 1**
- 鍛戒腑鐗囨鐢?`<mark>` 楂樹寒
- 鏁版嵁婧愶細`/search.json`锛堟瀯寤烘湡鐢熸垚锛?
### 7.2 鎼滅储妗嗕綅缃?
`/search/` 鍏ㄧ珯鎼滅储椤点€傚闇€鍦ㄥ叾瀹冮〉闈㈠姞鎼滅储妗嗭紝澶嶇敤 `search.html` 涓殑 input + 寮曞叆 `search.js`銆?
### 7.3 `search.json` 鏁版嵁鏍煎紡

```json
{
  "title": "瀵掗湶锛氱娣遍湶閲嶏紝娑﹁偤鍏婚槾",
  "url": "/-shiyan-/2026/10/08/hanlu-yanfei/",
  "lang": "zh-CN",
  "tags": ["瀵掗湶", "鑺傛皵", "娑﹁偤", "鍏婚槾", "绉嬪"],
  "category": "jieqi",
  "excerpt": "...",
  "content": "..."
}
```

> 褰撳墠 `search.json` 鍖呭惈鍏ㄩ儴 105 绡囥€?*鎼滅储鏄叏璇娣峰悎鐨?*锛堜笉鍋氳绉嶈繃婊わ級锛屽闇€鍒嗚绉嶉渶瑕佹媶鍒嗘暟鎹?+ 澶氫唤绱㈠紩銆?
---

## 8. 涓婚

### 8.1 鍙ら瑙嗚

| 椤?| 鍊?|
| --- | --- |
| 搴曡壊 | 瀹ｇ焊绫抽粍 `#f5efe1`锛堟槑锛?/ 澧ㄨ壊 `#1a1410`锛堟殫锛?|
| 寮鸿皟鑹?| 鏈辩孩 `#a82a2a`銆侀粵闈?`#2d4a4f` |
| 瀛椾綋 | 妤蜂綋锛坄Ma Shan Zheng`锛?+ 瀹嬩綋锛坄Noto Serif SC`锛?+ 榫欒棌锛堥鑺憋級 |
| 鍥炬爣 | 鑷粯 SVG锛堝嵃绔犮€佽妭姘斻€佸垎绫伙級 |
| 瑁呴グ | hero 鍗扮珷 / 鍗疯酱鍒嗛殧绾?/ 鑺傛皵寰界珷 |

### 8.2 鏄?/ 鏆椾富棰?
- 鎵嬪姩鍒囨崲锛坔eader 澶槼 / 鏈堜寒鎸夐挳锛? 璺熼殢绯荤粺
- 鐘舵€佸啓鍏?`localStorage('theme')`
- `head.html` 椤堕儴 inline 鑴氭湰棰勮缃?`data-theme`锛?*閬垮厤 FOUC**

---

## 9. 閮ㄧ讲 CI/CD

### 9.1 娴佺▼

```
push main
  鈫?.github/workflows/jekyll.yml
  鈫?checkout 鈫?setup-ruby 3.2 鈫?bundle install
  鈫?bundle exec jekyll build --trace
  鈫?upload artifact (.github-pages deploy-pages)
  鈫?鎺ㄩ€?_site 鍒?GitHub Pages
```

### 9.2 鍏抽敭閰嶇疆

- `Gemfile` 鐢?`github-pages` gem锛堢櫧鍚嶅崟鍐呮彃浠讹級
- `_config.yml` 鐨?`exclude` 鎺掗櫎 README銆丟emfile銆乥uild_logs銆乣scripts` 绛?- 瑙﹀彂锛歚push` 鍒?`main`锛屾垨 `workflow_dispatch` 鎵嬪姩

### 9.3 鍚敤 Pages

浠撳簱 Settings 鈫?Pages 鈫?Source: **Deploy from a branch** 鈫?Branch: `main` / `(root)`

锛?*宸查厤缃?*銆傛瘡娆?push 鑷姩鏋勫缓绾?1鈥? 鍒嗛挓銆傦級

---

## 10. 鏈湴寮€鍙?
```bash
# 瀹夎渚濊禆锛堥渶瑕?Ruby 2.7+锛?bundle install

# 鍚姩鏈湴鏈嶅姟
bundle exec jekyll serve

# 璁块棶 http://127.0.0.1:4000/-shiyan-/
```

> Windows 涓婅嫢 Gem 鎱㈠彲鎹㈡簮锛?> `bundle config mirror.https://rubygems.org https://gems.ruby-china.com`

淇敼 `_config.yml` / `_layouts` / `_includes` 鍚?Jekyll 浼氱儹閲嶈浇锛堝閲忔瀯寤猴級銆備慨鏀?`_data/*.yml` 涔熸敮鎸佺儹閲嶈浇銆?
---

## 11. 甯哥敤鎿嶄綔

### 11.1 娣诲姞涓€绡囨簮鏂囩珷锛坺h-CN锛?
1. 鍦?`_posts/` 鏂板缓 `YYYY-MM-DD-slug.md`
2. 鍐?front matter锛?*鏄惧紡鍚?`lang: zh-CN`**锛? 姝ｆ枃
3. 璺?`python tools/generate_archives.py` 閲嶇敓鎴愬垎绫?鏍囩椤?4. `git add` + `git commit` + `git push`

### 11.2 娣诲姞涓€绡囨枃绔犵殑 6 璇缈昏瘧

1. 鍦?`en/_posts/`, `ar/_posts/`, ... 绛?6 涓瓙鐩綍鍚勫缓鍚屽悕 `.md` 鏂囦欢
2. front matter 鏀?`lang: <code>` + `permalink: /<code>/YYYY/MM/DD/<slug>/`锛坄ar` 鍔?`dir: rtl`锛?3. 缈昏瘧姝ｆ枃锛屾湳璇牸寮忥細`<native>锛堟眽瀛? p墨ny墨n, English锛塦
4. 鏂囨湯鍔?`<!-- Translated by translation-specialist agent -->`
5. 鎺ㄩ€?
### 11.3 淇敼鍒嗙被

1. 缂栬緫 `_data/categories.yml`锛坰lug / name / desc / color / icon锛?2. 缂栬緫 `_data/categories-i18n.yml`锛? 璇 name + desc锛?3. 璺?`python tools/generate_archives.py`
4. 鎺ㄩ€?
### 11.4 淇敼椤堕儴瀵艰埅

1. 缂栬緫 `_data/nav.yml`锛圲RL 涓庡浘鏍囷級
2. 缂栬緫 `_data/nav-i18n.yml`锛? 璇鏍囬锛?3. 鎺ㄩ€?
### 11.5 娣诲姞鏂拌绉嶏紙浠ヨ憽璇?`pt` 涓轰緥锛?
闇€瑕佸悓姝ヤ慨鏀?8 澶勶細

1. `_config.yml` 鈫?`supported_langs` 鍔?`pt`
2. `_data/i18n.yml` 鈫?`langs` 鍔?pt 椤?+ `strings.pt` 瀹屾暣瀛楁
3. `_data/nav-i18n.yml` 鈫?姣忔潯 nav 鍔?`pt: ...`
4. `_data/categories-i18n.yml` 鈫?姣忎釜鍒嗙被鍔?`pt: name + desc`
5. `assets/js/i18n.js` 鈫?`SUPPORTED` 鏁扮粍鍔?`'pt'`
6. 鑻ユ柊璇鏄?RTL锛宍_config.yml` 鐨?`rtl_langs` 鍔?`pt`锛岀炕璇戞枃浠跺姞 `dir: rtl`
7. `pt/_posts/` 鐩綍 + 缈昏瘧鏂囦欢
8. `pt/index.md` / `pt/archive.md` / `pt/categories.md` / `pt/tags.md` / `pt/search.md` / `pt/about.md` / `pt/about-zhongyi.md`

### 11.6 淇敼榛樿璇

`_config.yml` 鈫?`default_lang: <code>`銆傚悓鏃讹細

- 鎶婂搴旇绉嶇殑婧愭枃绔犱粠瀛愮洰褰曠Щ鍥?`_posts/` 鏍圭洰褰?- 鍏朵綑璇浣滀负缈昏瘧鐗?- 淇敼鎵€鏈?`_layouts/*.html` 涓 `site.default_lang` 鐨勫紩鐢紙搴旇嚜鍔ㄩ€傞厤锛?
---

## 12. 鏁呴殰鎺掓煡

### 12.1 鏈潵鏃ユ湡鏂囩珷 404锛? 璇鍏?404锛?
**鐥囩姸**锛歚2026-10-08` 閭ｇ瘒鏁寸瘒 6 璇閮?404锛屼絾鍚屾湀鍏朵粬鏃ユ湡姝ｅ父銆?
**鍘熷洜**锛歚_config.yml` 榛樿 `future: false`锛孞ekyll 榛橀粯璺宠繃鏈潵鏃ユ湡鐨?post銆?
**淇硶**锛歚_config.yml` 鎶?`future: false` 鏀逛负 `future: true`銆?
### 12.2 棣栭〉鍙湅鍒?1 绡囨枃绔狅紙鍏朵粬 14 绡囨秷澶憋級

**鐥囩姸**锛氶椤?/ 褰掓。 / 鍒嗙被 / 鏍囩椤靛彧鏄剧ず 1 绡?zh-CN 鏂囩珷銆?
**鍘熷洜**锛堜换涓€鍗冲彲瑙﹀彂锛夛細

1. 婧愭枃绔犳病鍐?`lang: zh-CN` 瀛楁 鈫?`where: 'lang', 'zh-CN'` 杩囨护澶辫触
2. 鐢ㄤ簡 Jekyll 鍒嗛〉 `paginator.posts`锛坧aginator 鍙?105 绡囧墠 10锛岃繃婊ゅ悗鍙墿 1 绡囨簮 hanlu锛?
**淇硶**锛?
1. 缁欐墍鏈夋簮鏂囩珷鍔?`lang: zh-CN`锛堢敤 PowerShell 鑴氭湰鎵归噺鍔狅級
2. home.html **涓嶈鐢?paginator**锛屾敼鐢?`site.posts | where: 'lang', cur_lang | limit: 10`

### 12.3 鍒囪瑷€ 404

**鐥囩姸**锛氱偣璇█鍒囨崲鍣ㄨ烦杞埌 404銆?
**鍘熷洜**锛氭棫鐗?`i18n.js` 娌¤€冭檻 `baseurl: /-shiyan-`锛屾嫾鍑?`/en/-shiyan-/...` 杩欑 URL銆?
**淇硶**锛?
- `_layouts/default.html` 鐨?`<html>` 鍔?`data-baseurl="{{ site.baseurl }}"`
- `assets/js/i18n.js` 鐢?`getBaseurl()` 璇昏灞炴€э紝鍓?baseurl 鍚庡啀鎷艰绉嶅墠缂€

### 12.4 鍒囪瑷€鍚庢柟鍚戞病鍙橈紙闃挎媺浼锛?
**鐥囩姸**锛氶€変簡 AR 浣嗛〉闈㈡病鍙?RTL銆?
**淇硶**锛?
- `_config.yml` 鐨?`rtl_langs` 鍚?`ar`
- AR 缈昏瘧鏂囦欢鐨?front matter 鍚?`dir: rtl`
- `_layouts/default.html` 鐨?RTL 鏉′欢鍒嗘敮姝ｅ父宸ヤ綔

### 12.5 CDN 缂撳瓨鐪嬩笉鍒版洿鏂?
**鐥囩姸**锛歝ommit 宸?push銆乥uild 鎴愬姛锛屼絾椤甸潰鐪嬭捣鏉ユ病鍙樸€?
**淇硶**锛?
- GitHub Pages 杈圭紭缂撳瓨榛樿 600 绉?- 绛?10 鍒嗛挓鍐嶈闂?- 璋冭瘯鏃剁敤 `?cb=<timestamp>` 缁曡繃缂撳瓨
- 鐢?`Invoke-WebRequest -Headers @{Cache-Control='no-cache'}` 寮哄埗

### 12.6 鏋勫缓澶辫触

- 鐪?GitHub Actions 鏃ュ織锛歨ttps://github.com/xiebingcheng/-shiyan-/actions
- 甯歌鍘熷洜锛?  - **YAML 閿欒**锛坒ront matter 鎴?`_data/*.yml`锛夆€斺€?Jekyll 榛樿 warn 涓嶆姤閿欙紝浣嗗彲鑳藉鑷?post 璺宠繃
  - **Liquid 妯℃澘閿欒**锛坄{{ ... }}` 鎴?`{% ... %}`锛夆€斺€?鐢?`bundle exec jekyll build --trace` 鏌?  - **鎻掍欢涓嶅湪鐧藉悕鍗?* 鈥斺€?鏀圭敤鍐呯疆 `jekyll-*` 鎻掍欢
  - **鏂囦欢鍚嶆棩鏈熸牸寮忎笉瀵?*锛堥潪 `YYYY-MM-DD-` 寮€澶达級

### 12.7 鍒囨崲鍣ㄦ病鏄剧ず / 璇娌″嚭鐜?
- 妫€鏌?`<html>` 鐨?`data-baseurl` 灞炴€?- 妫€鏌?`_data/i18n.yml` 鐨?`langs` 鍒楄〃鏄惁鍚洰鏍囪绉?- 妫€鏌?`assets/js/i18n.js` 鐨?`SUPPORTED` 鏁扮粍
- 妫€鏌?`assets/js/i18n.js` 鐨?`RTL` 鏁扮粍锛堜粎 RTL 璇锛?
### 12.8 鎼滅储涓嶅埌鏂版枃绔?
- `_config.yml` 涓?`search.enabled: true`
- 鏋勫缓鍚?`search.json` 鏄惁鏇存柊锛堟棫 Jekyll 鍙兘缂撳瓨 `_site`锛?- 鐩存帴璁块棶 `/search.json?cb=<ts>` 鐪嬫槸鍚﹀惈鏂版枃绔?
### 12.9 鍒嗙被/鏍囩椤垫病鏇存柊

娣诲姞 / 淇敼鏂囩珷鍚庡繀椤昏窇锛?
```bash
python tools/generate_archives.py
```

鍚﹀垯 `categories/<slug>.md` 鍜?`tags/<tag>.md` 涓嶄細鏇存柊銆?
---

## 13. 椤圭洰缁撴瀯閫熸煡

```
.
鈹溾攢鈹€ _config.yml                 # 绔欑偣閰嶇疆 + i18n + defaults
鈹溾攢鈹€ _data/                      # YAML 鏁版嵁
鈹?  鈹溾攢鈹€ categories.yml          # 鍒嗙被鍏冩暟鎹紙slug / name / desc / color / icon锛?鈹?  鈹溾攢鈹€ categories-i18n.yml     # 鍒嗙被 7 璇 name + desc
鈹?  鈹溾攢鈹€ i18n.yml                # 璇鍏冧俊鎭?+ UI 瀛楃涓?鈹?  鈹斺攢鈹€ nav-i18n.yml            # 瀵艰埅 7 璇鏍囬
鈹溾攢鈹€ _layouts/                   # 11 涓竷灞€
鈹溾攢鈹€ _includes/                  # 7 涓粍浠?鈹溾攢鈹€ _posts/                     # 15 绡囨簮鏂囩珷锛坙ang: zh-CN锛?鈹溾攢鈹€ en/ ar/ ru/ fr/ es/ id/     # 6 涓绉嶅瓙鐩綍
鈹?  鈹溾攢鈹€ _posts/                 # 鍚勮绉嶇炕璇戞枃绔?鈹?  鈹斺攢鈹€ index.md, archive.md, ...
鈹溾攢鈹€ categories/                 # 6 涓垎绫婚〉锛堣剼鏈敓鎴愶紝浠?zh锛?鈹溾攢鈹€ tags/                       # 55 涓爣绛鹃〉锛堣剼鏈敓鎴愶紝浠?zh锛?鈹溾攢鈹€ about.md, about-zhongyi.md, archive.md, categories.md, tags.md, search.md
鈹溾攢鈹€ index.html                  # zh-CN 棣栭〉
鈹溾攢鈹€ search.json                 # 鎼滅储鏁版嵁锛堟瀯寤烘湡鐢熸垚锛?鈹溾攢鈹€ feed.xml                    # RSS锛坖ekyll-feed 鑷姩锛?鈹溾攢鈹€ sitemap.xml                 # sitemap锛坖ekyll-sitemap 鑷姩锛?鈹溾攢鈹€ assets/
鈹?  鈹溾攢鈹€ css/main.css
鈹?  鈹溾攢鈹€ js/{theme,nav,i18n,search}.js
鈹?  鈹斺攢鈹€ img/*.svg
鈹溾攢鈹€ tools/
鈹?  鈹溾攢鈹€ generate_archives.py    # 鍒嗙被/鏍囩椤电敓鎴?鈹?  鈹溾攢鈹€ gen_pages.py            # 椤甸潰鐢熸垚锛堟棫锛?鈹?  鈹溾攢鈹€ fix_yaml.py             # YAML 淇锛堟棫锛?鈹?  鈹斺攢鈹€ add_lang_field.py       # lang 瀛楁娣诲姞锛堟棫锛?鈹溾攢鈹€ .github/workflows/
鈹?  鈹斺攢鈹€ jekyll.yml              # GitHub Actions 閮ㄧ讲
鈹溾攢鈹€ Gemfile                     # github-pages gem
鈹溾攢鈹€ robots.txt
鈹溾攢鈹€ README.md                   # 閮ㄧ讲涓庢湰鍦伴瑙?鈹斺攢鈹€ FUNCTIONALITY.md            # 鏈枃浠?```

---

**鏈€杩戝彉鏇?*锛?
- `c227583` home 鏀圭敤 `site.posts | where | limit 10` 鍙栦唬 paginator
- `e1e7db8` 婧愭枃绔犳樉寮忓姞 `lang: zh-CN` + layout 鐢ㄧ畝鍗?`where`
- `914d054` 鎵€鏈?list layout 鎸?`page.lang` 杩囨护
- `85c1f9f` 寮冪敤 `where_exp + empty` 鏂规锛堣涓轰笉绋筹級
- `6805c07` `future: true` + `i18n.js` 鏀寔 baseurl
