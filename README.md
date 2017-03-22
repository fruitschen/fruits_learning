# fruits_learning

个人项目，学编程并实现了一些自己需要的功能。项目是用[wagtail][wagtail]创建的。

Personal project. Learning stuff, implemented some features I need to use myself.
project created with [wagtail][wagtail].

---

# info_collector app

定期从一些信息源(InfoSource)抓取信息，使用到:

regularly crawl content from InfoSource, using:

* [rq][rq]
* [django-rq][django-rq]
* [rq-scheduler][rq-scheduler]
* [supervisord][supervisord]

API:

[django-rest-framework][django-rest-framework]

前端使用ReactJS显示，用到

frontend implemented with:

* [React][react]
* [ant.design][ant-design]
* [django-webpack-loader][django-webpack-loader]

---

# feed reader app

集成了[django-feed-reader][django-feed-reader]，用React重写了前端的代码。

integrated [django-feed-reader][django-feed-reader], frontend written with ReactJS.


---

# stocks app

一些自用的股票投资功能，包括配对交易记账，公开账户等等。主要用到：

some stocks features I need myself, including pair transaction, public accounts, etc.
It's mainly built with:

* [jQuery v3.1.1][jquery]
* [bootstrap 3.3.7][bootstrap]
* [echarts 3.4][echarts]


[wagtail]: https://wagtail.io/
[rq]: https://github.com/nvie/rq
[django-rq]: https://github.com/ui/django-rq
[rq-scheduler]: https://github.com/ui/rq-scheduler
[supervisord]: http://supervisord.org/
[django-rest-framework]: http://www.django-rest-framework.org/
[react]: https://facebook.github.io/react/
[ant-design]: https://ant.design/
[django-webpack-loader]: https://github.com/owais/django-webpack-loader
[django-feed-reader]: https://github.com/ahernp/django-feedreader
[jquery]: https://jquery.com/
[bootstrap]: http://getbootstrap.com/
[echarts]: https://github.com/ecomfe/echarts
