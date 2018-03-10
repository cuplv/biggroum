All the data is in a big json file.

I skipped the binary file representation and I used the jsons that we already get from Solr.
The format could change in the future, but the "semantic" of the data should still be the same.

The json file contains three different kinds of json documents.


# Description on the doc types

1) Pattern

This is a pattern of API usages.

It contains:
  - The type of the document (doc_type_sni field).
    For a pattern its value is "pattern"
  - The list of groums id used to compute the pattern (groum_keys_t field).
  - The type of the pattern (type_sni field)
    The value can be:
    - popular: the "correct" usage
    - anomalous: this is a possible bug
    - isolated: this is a possible bug
  - The graph representing the pattern in dot format (groum_dot_sni field)
  - The first date the pattern was found in the corpus (lower_date_sni field, the date is in ISO 8601 format)
  - The last date the pattern was found in the corpus (upper_date_sni field, the date is in ISO 8601 format)
  - The frequency of the pattern (in how many groums we found the pattern, frequency_sni field)
  - id: the id of the document (it is unique)

  I saw some discrepancies between the length of the list of groums and the frequency in some example (they should be the same)
  Let's start with the data we have, I can double check the cause of this error later on.

  You should look at the lower and upper date for the trend analysis.

 {
        "groum_keys_t": [
          "evgenius/campyre/f92adfeb4ab723bf6a0394a5d8be53abf956560f/campyre.android.RoomTabs/transcriptIntent",
          "evgenius/campyre/f92adfeb4ab723bf6a0394a5d8be53abf956560f/campyre.android.ShareImage/onLogin",
          "evgenius/campyre/f92adfeb4ab723bf6a0394a5d8be53abf956560f/campyre.android.Utils/feedbackIntent",
          "qylk/AudioPlayer/ddcb0e819c726f3028048f29fface8084bd5d9c1/cn.qylk.fragment.Fragment_VideoList/onItemClick",
          "braintree/braintree_android/44e20eed28af498e980202f9f12579911be6e249/com.braintreepayments.api.PaymentRequest/getIntent",
          "braintree/braintree_android/44e20eed28af498e980202f9f12579911be6e249/com.braintreepayments.api.ThreeDSecure$2$1/success",
          "yukuku/androidbible/f105d6af26c769fd84eb3b3d9678d79f2b3a0106/com.example.android.wizardpager.MainActivity/createIntent",
          "Awful/Awful.apk/b442bf67243174a5335b61d3e44a1df8378459ea/com.ferg.awful.PrivateMessageListFragment$2/onItemClick",
          "geel9/FPAndroid/1e8da50a4ed6da940534c73f7682b807fd869722/com.geel9.facepunch.FPActivity$3$1$1/onResult",
          "learning-android/Yamba/46795d3c4a1f56416f88a18b708d9db36a429025/com.marakana.android.yamba.TimelineFragment/onListItemClick",
          "Pushwoosh/pushwoosh-android-sdk/c77907185161325fbb777a376a2abaf6621fce44/com.pushwoosh.PushManager/setBeaconBackgroundMode",
          "Pushwoosh/pushwoosh-android-sdk/c77907185161325fbb777a376a2abaf6621fce44/com.pushwoosh.location.GeoLocationService/a",
          "Pushwoosh/pushwoosh-android-sdk/c77907185161325fbb777a376a2abaf6621fce44/com.pushwoosh.location.GeoLocationService/b",
          "jiaxianhua/imame4all/43ddfff99e4f4e6931ed14958200cd1ba3a05099/com.seleuco.mame4all.prefs.DefineKeys/onListItemClick",
          "jiaxianhua/imame4all/43ddfff99e4f4e6931ed14958200cd1ba3a05099/com.seleuco.mame4all.prefs.ListKeys/onListItemClick",
          "SiPlus/Steamshots/865c956c8c93cf966683535e7699a7b9a6bc81a8/com.steamcommunity.siplus.steamscreenshots.Authenticator/addAccount",
          "SiPlus/Steamshots/865c956c8c93cf966683535e7699a7b9a6bc81a8/com.steamcommunity.siplus.steamscreenshots.LoginSelectActivity/onOptionsItemSelected",
          "SiPlus/Steamshots/865c956c8c93cf966683535e7699a7b9a6bc81a8/com.steamcommunity.siplus.steamscreenshots.LoginSelectOnItemClick/onItemClick",
          "thenewcircle/class-3177/5385c4b383ebf60fbd26e5d1c4cf4b3f3642273a/com.twitter.yamba.TimelineFragment/onListItemClick",
          "zackehh/RSSDemo/c15a19cb13dae4887a0d4293f190181548b92863/com.zackehh.rssdemo.ListActivity$1/onItemClick",
          "zackehh/RSSDemo/c15a19cb13dae4887a0d4293f190181548b92863/com.zackehh.rssdemo.PostActivity$1/onReceivedError",
          "cqq/YunBa-Yo/fbe49bbfdf3d5b1a8db347ec7b01f2101c3cd961/io.yunba.yo.activity.LoginActivity$1/onSuccess",
          "RemiKoutcherawy/OriSim3D-Android/4c7670b43f36425fdddcf493f309117ab6095f28/rk.or.android.ModelSelection/onItemClick",
          "google/vpn-reverse-tether/304749e5c11d0466cfeef3220c91e91401c53167/vpntether.StartActivity/onActivityResult",
          "ispedals/FloatingJapaneseDictionary/143f31b364a4b7a21aebdf982ac2abd6e5d4acc4/wei.mark.standout.StandOutWindow/getCloseIntent",
          "ispedals/FloatingJapaneseDictionary/143f31b364a4b7a21aebdf982ac2abd6e5d4acc4/wei.mark.standout.StandOutWindow/getHideIntent",
          "ispedals/FloatingJapaneseDictionary/143f31b364a4b7a21aebdf982ac2abd6e5d4acc4/wei.mark.standout.StandOutWindow/getShowIntent",
          "evgenius/campyre/f92adfeb4ab723bf6a0394a5d8be53abf956560f/campyre.android.RoomList/selectRoom",
          "evgenius/campyre/f92adfeb4ab723bf6a0394a5d8be53abf956560f/campyre.android.MessageAdapter$1/onClick",
          "evgenius/campyre/f92adfeb4ab723bf6a0394a5d8be53abf956560f/campyre.android.MessageAdapter$2/onClick",
          "voituk/SponsorPayDemo/5be01f49f76607651f76fda818eab9df68b8be5d/com.voituk.sponsorpay.SponsorPayDemoActivity/onClick",
          "SiPlus/Steamshots/865c956c8c93cf966683535e7699a7b9a6bc81a8/com.steamcommunity.siplus.steamscreenshots.ScreenshotsActivity/onCreate",
          "evgenius/campyre/f92adfeb4ab723bf6a0394a5d8be53abf956560f/campyre.android.RoomTabs/roomIntent",
          "msgilligan/RosieWalletAndroid/4adca0461ad9d1778153e7e07ac7f065b390a14c/com.rosiewallet.MainActivity/GetUnspentStart",
          "msgilligan/RosieWalletAndroid/4adca0461ad9d1778153e7e07ac7f065b390a14c/com.rosiewallet.MainActivity/GetValueStart",
          "msgilligan/RosieWalletAndroid/4adca0461ad9d1778153e7e07ac7f065b390a14c/com.rosiewallet.MainActivity/resultSendCoinRivet",
          "SiPlus/Steamshots/865c956c8c93cf966683535e7699a7b9a6bc81a8/com.steamcommunity.siplus.steamscreenshots.ScreenshotsImagesOnItemClick/onItemClick",
          "braintree/braintree_android/44e20eed28af498e980202f9f12579911be6e249/com.braintreepayments.api.BraintreeFragment/flushAnalyticsEvents",
          "gorbin/ASNE/7e2f60afb95a4ebf6a9af0036cad34dcc8486ff1/com.github.gorbin.asne.instagram.InstagramSocialNetwork/initInstagramLogin",
          "gorbin/ASNE/7e2f60afb95a4ebf6a9af0036cad34dcc8486ff1/com.github.gorbin.asne.twitter.TwitterSocialNetwork$RequestLoginAsyncTask/onPostExecute",
          "twitter-university/AntiMalware/4a9991e44457b08ab508a22f39ab90b6c80dc18b/com.marakana.android.antimalware.ScanService/scan",
          "ramdroid/androiddev/2607b7d2f6a7824267b1088a6681f4a78e01766e/com.ramdroid.androiddev.ParcelableDemo.SomeActivity/doSomething",
          "zhaoshouren/ZS-DeskClock/5c9d923170f82e98c7755a26a61dd5ab4627fc7e/com.zhaoshouren.android.apps.clock.ui.AlarmAlertActivity/handleScreenOff",
          "ws72/VIPMediaPlayer/013817e0d795c21c12a4d6ad4eb90e94622dca9f/com.mx.vipmediaplayer.VIPPlayerActivity/onCreate",
          "ispedals/FloatingJapaneseDictionary/143f31b364a4b7a21aebdf982ac2abd6e5d4acc4/wei.mark.standout.StandOutWindow/getSendDataIntent",
          "cqq/YunBa-Yo/fbe49bbfdf3d5b1a8db347ec7b01f2101c3cd961/io.yunba.yo.activity.SplashActivity/onCreate"
        ],
        "upper_date_sni": "2016-09-14T09:55:04Z",
        "groum_dot_sni": "digraph isoX {\n node[shape=box,style=\"filled,rounded\",penwidth=2.0,fontsize=13,]; \n\t edge[ arrowhead=onormal,penwidth=2.0,]; \n\n\"n_4\" [shape=ellipse,color=red,style=dashed,label=\"DataNode #4: android.content.Intent  $r0\"];\n\"n_1\" [shape=ellipse,color=red,style=dashed,label=\"DataNode #1: campyre.android.RoomTabs  this\"];\n\"n_7\" [shape=ellipse,color=red,style=dashed,label=\"DataNode #7: java.lang.Class  class \\'campyre/android/TranscriptView\\'\"];\n\"n_8\" [ shape=box, style=filled, color=lightgray, label=\" android.content.Intent.<init>[#4](#1, #7)\"];\n\"n_14\" [shape=ellipse,color=red,style=dashed,label=\"DataNode #14: android.content.Intent  $r2\"];\n\"n_13\" [shape=ellipse,color=red,style=dashed,label=\"DataNode #13: java.lang.String  \\'room_id\\'\"];\n\"n_11\" [shape=ellipse,color=red,style=dashed,label=\"DataNode #11: java.lang.String  $r1\"];\n\"n_15\" [ shape=box, style=filled, color=lightgray, label=\" android.content.Intent.putExtra[#4](#13, #11)\"];\n\"n_15\" -> \"n_14\"[color=blue, penwidth=2];\n\"n_4\" -> \"n_15\"[color=green, penwidth=2];\n\"n_11\" -> \"n_15\"[color=green, penwidth=2];\n\"n_4\" -> \"n_8\"[color=green, penwidth=2];\n\"n_13\" -> \"n_15\"[color=green, penwidth=2];\n\"n_7\" -> \"n_8\"[color=green, penwidth=2];\n\"n_1\" -> \"n_8\"[color=green, penwidth=2];\n\"n_8\" -> \"n_15\"[color=black, penwidth=3];\n } \n",
        "type_sni": "popular",
        "doc_type_sni": "pattern",
        "frequency_sni": "73",
        "lower_date_sni": "2011-11-12T19:58:06Z",
        "cluster_key_sni": "79",
        "id": "79/popular/1",
        "_version_": 1570738120205271000
      }

2) Groum
A groum for a single method declaration.

The groum document contains:
  - id: the unique id of the groum
  - The type of the document (doc_type_sni)
    It is groum for a groum
  - The Java file were the method is declared
  - The complete and unambiguous name of the class (class_name_t)
    IF you see a $<n> at the end of the name, this is an anonymous inner class
  - The name of the method (method_name_t)
    <init> is the name given to the constructor
  - The name of the package (package_name_sni)
  - The line number of the method declaration in the file (method_line_number_sni)
  - The class line number in the file (class_line_number_sni)
  - The source code (in Jimple, an intermediate representation, in the field jimple_sni)
  - The commit hash (hash_sni)
  - The date of the commit (commit_date, in ISO 8601)
  - The user and repo name on github (repo_sni)
  - The url of the repo on github (github_url_sni)
  - The dot representation of the groum (groum_dot_sni)
  
  {
        "filename_t":["FriendList.java"],
        "repo_sni":"heinrisch/Contact-Picture-Sync",
        "package_name_sni":"heinrisch.contact.picture.sync",
        "groum_dot_sni":"digraph \"cfg\" {\n    label=\"cfg\";\n    label=\"heinrisch.contact.picture.sync.FriendList$5.<init>\";\n    node [shape=box];\n    \"0\" [label=\"(#0)\",group=0,];\n    \"5\" [label=\"(#5)\",group=0,];\n    \"9\" [label=\"(#9)\",group=0,];\n    \"10\" [label=\"(#10)\",group=0,];\n    \"9\"->\"10\" [color=black,Damping=0.7,];\n    \"7\" [label=\"this.<set>.heinrisch.contact.picture.sync.FriendList$5.this$0_heinrisch.contact.picture.sync.FriendList()\\n(#1).(#7)()\",group=0,];\n    \"5\"->\"7\" [color=black,Damping=0.7,];\n    \"8\" [label=\"this.android.os.Handler.<init>()\\n(#1).(#8)()\",group=0,];\n    \"7\"->\"8\" [color=black,Damping=0.7,];\n    \"8\"->\"9\" [color=black,Damping=0.7,];\n    \"2\" [label=\"(#2)\",group=0,];\n    \"0\"->\"2\" [color=black,Damping=0.7,];\n    \"2\"->\"5\" [color=black,Damping=0.7,];\n    \"4\" [label=\"this$0 : heinrisch.contact.picture.sync.FriendList (# 4)\",style=dashed,shape=ellipse,group=1,];\n    \"4\"->\"7\" [color=red,Damping=0.7,];\n    \"1\" [label=\"this : heinrisch.contact.picture.sync.FriendList$5 (# 1)\",style=dashed,shape=ellipse,group=1,];\n    \"1\"->\"8\" [color=red,Damping=0.7,];\n    \"1\"->\"7\" [color=red,Damping=0.7,];\n    \"2\"->\"1\" [color=blue,];\n    \"5\"->\"4\" [color=blue,];\n}\n",
        "github_url_sni":"https://github.com/heinrisch/Contact-Picture-Sync",
        "jimple_sni":"    void <init>__sliced__(heinrisch.contact.picture.sync.FriendList)\n    {\n        heinrisch.contact.picture.sync.FriendList$5 this;\n        heinrisch.contact.picture.sync.FriendList this$0;\n\n        nop;\n\n        this := @this: heinrisch.contact.picture.sync.FriendList$5;\n\n        this$0 := @parameter0: heinrisch.contact.picture.sync.FriendList;\n\n        this.<heinrisch.contact.picture.sync.FriendList$5: heinrisch.contact.picture.sync.FriendList this$0> = this$0;\n\n        specialinvoke this.<android.os.Handler: void <init>()>();\n\n        goto label1;\n\n     label1:\n        nop;\n    }\n",
        "class_line_number_sni":"0",
        "method_line_number_sni":"270",
        "hash_sni":"ca1d34374b6561055e69d6424284be65ad244fcb",
        "id":"heinrisch/Contact-Picture-Sync/ca1d34374b6561055e69d6424284be65ad244fcb/heinrisch.contact.picture.sync.FriendList$5/<init>",
        "commit_date_sni":"2013-01-07T08:36:19Z",
        "method_name_t":["<init>"],
        "doc_type_sni":"groum",
        "class_name_t":["heinrisch.contact.picture.sync.FriendList$5"],
        "_version_":1570701698528182272}

3) Cluster
A cluster groups the groums that use frequently a subset of methods.

The cluster document contains:
  - id: the unique id of the cluster (usually, an integer)
  - The type of the document (doc_type_sni). Its value is "cluster"
  - methods_in_cluster_t: list of method calls contained in the cluster
  - patterns_keys_t: list of patterns mined from this cluster
  - groums_keys_t: list of groums grouped in the cluster
