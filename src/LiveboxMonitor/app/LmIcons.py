### Livebox Monitor icons module ###

import base64

from PyQt6 import QtGui


# ############# Icons #############

class LmIcon:

    AppIconPixmap = None
    AppIconData = '''
        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'''

    TickPixmap = None
    TickData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAxlBMVEUAAAAAAAAAqhUAXQJU32UA
        oBIAlA8AhwwPyx8XyygjwDYAmhEAjQ4AXQIAqhUApRQAfQoASgIAqhUAqBQAbQYADgEAAAAAqRUA
        AABP2mAIkhIHkhBGz1dO1l8R0SIR2SIRyCI9xU7n5+fj4+MRviIRtSLe3t5d5W5c5G3X19c3v0gS
        niMRriJP12BBylIxukInsDgbqSwRsiIRqiIRpyIRoiL////4+Pjr6+ui16me4qcww0EttT4rszwg
        xjEcpC0XrygSoiOQ/0eIAAAAHHRSTlMAGczM+8zMzPn83czMvLq6uoNzc3MzEgwJ+d3dEPRlegAA
        AKNJREFUGNNlyNcSwVAUQNEgiPSe4IpUpHe9/v9POTcyZoz1tjfxz5D5YY+XDRgKTW7BDpC0AkMg
        V19zAcaYRB9RhtIxHqnTyfdnB+HBoOga5cXD89y4YGBM0O1QvuINdFtO8MhO4bGBbuv6iQd7ScIQ
        ugkAC2N69xPoxMemeMxsu3Iru4OHOLMsK7A6lAhDXVDrHrVUCULXJG7U4yRNJ8zBD/MNwiEWhSUh
        NaMAAAAASUVORK5CYII='''

    CrossPixmap = None
    CrossData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJ
        bWFnZVJlYWR5ccllPAAAAe5JREFUeNqkk89KG1EUxr+ZubnUjJaipgtNtTZKxE1AVIi4yM5tF30H
        oe/iA3TnQkTBRbZFKApCAl1142CJqLR0ZUNJJpPJZP70nJvcEK0SpAPfzD3n5vedM2dujCRJ8D+X
        ODIMGMA4aYfibdLkCKZO+kxlP5FcwRla7MytrHxcLhazMp2WT5HcbeB5gVOp5H44Dqd2RdTb217a
        2Mi6vi/h+6O6lu9WV7M3jsPd7ppsQJqMTVO6rgtWdn8fev1YrpskkhlmzZBuLJ8qN5tNLJfLqgw/
        OX4sxyaaE2G/L8/z0Gq1cLy4iA+1mjKcOzhQ+RrFpmniy9oaUqkUMpkMNDcwCIIAYRhiwraxNz2N
        wskJLMtSgJQSZwSr6Xa7aDca/xowHFB7Xr0OO47vwazx4W9PJpozu2xK6hCY3N1hLIqQPz29Bwsh
        ULq8RJp+x5JUTHODIRpkkKbv/GYI/ra+jq+FgjJgbV5dKYMX1KHmBh1ImgFv3pZKCr4geJZiVjWf
        V+2e53K9LqiQ5kSnfzwjmuIY+cxT8J3g+aF35nWVYJ1rx3HQ6R1pWNd0ewu8bkdRfkYI2zYMi/8M
        4oF0juGq7//8FUWHh0DF4L2XwMIW8H4KKFL8asRR/vObwHOg3ACu2YA6x0S/wHMunmHzrwADAPb0
        7huzEp/RAAAAAElFTkSuQmCC'''

    DenyPixmap = None
    DenyData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAzFBMVEUAAAAAAACqAABdAADlXFzq
        YWGgAACUAACLAAAAAADLDw/vYmLGKSmTBweaAACEAABdAACqAAClAAB9AABKAACqAACoAABtAAAO
        AACpAAAAAADLFhaZMzP////48fHcuLjZERH1bGz/dnbhwcHChISrVlaeNjacMjLSExOyQ0PIERH2
        7e37c3PdX1+wQUHMQECnNTW/Ly+oKyvBISHQHx+9GhrAFRX5cXHtZWXZXFzhWVnNUFDDTU3bTEzC
        MTHRMDChLS2zKiq7JSWzHR3L21+eAAAAHHRSTlMAGszM/v3MzMwU+fnd3czMvLq6uoNzc3MzDAn5
        AP8ibQAAALhJREFUGNNlyEcSgjAUAFDUoIK90QzBSO8de7//ncyfYeGMb/m4f+pm0W0tNioLaTyi
        exDR0VhiseTRIfYdx48pQksWfZ5GvkWIaV951Iegp4RiQ9dD+3KGmNLEwgjGzNIpi8HRIQZO2RA3
        H0DwDtENfMcGcd8Qw1tm6mxKbD3rIcQjt0OYBn8aiFlVvWyTEAsHQTBjsdp6Xlm4blF7nrhiIU/E
        XUucyBwnKOt5rzVfKwKnCZ0fgvYFaUkWa6ms/VgAAAAASUVORK5CYII='''

    NotifPixmap = None
    NotifData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAArlBMVEUAAAAAAADLsgGWgAC1nQG8
        pAHDqgHMswHj0yL68p7g0EqVfwCslQDLsgHMswF3ZQCfiAAXEwAAAADMswEAAADj1S747ZK6pxC6
        pg3q3Cb76oHZ1Dfe1jLj2S3/9qj35nnz4nAAAADV0TzQz0D16YXw32n68Zz47ZDt6oH07Xp1dXVm
        Zmbq22HUzEjSyUXp4Wjt3WTe2GPl2VbV1FDa1E3k3EvX1Ebn3T4wMDAYGBhq6pIiAAAAGXRSTlMA
        GazMurWyYPj1x7utnZyDbzMSCgn39dnZsf32zgAAAJhJREFUGNNlyNcOgkAQQFFEYendgoA6C0jH
        3v7/x5wxGxPjebgPV/oXMkcWHBbiYIa+EXSD4bD19dfCxiHvt6htqZX8GTvUddSChlqVZdk/X8M4
        DieVRnHsrzlAji40lOLMOQfg6K7QOCSorhNCY3ZLEUBKZjQeGQLICA1rHqOmoWoWDm+pxYK28iQp
        8F1zKpiuH0jR5Ef0Bky6E46+fts4AAAAAElFTkSuQmCC'''

    CallOutPixmap = None
    CallOutData = '''
        iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAMAAABhEH5lAAABC1BMVEUAAAAnNldJlIBBhndBhHc9
        fHY+eXQvS2orOWcoNWglMVo0NF81TXoeIFAnK2oTDzceI04kMWgjNmZAfHc+d3QvYnU3Y25KkoQ1
        ZnM5a3I5bnM6YHk8a3w9bngyVWc7YXwmNlc0Vng3SGYnNlc1VXUzSmkuRW0pO14rPGAfJFEmM2Yi
        MVUrOGUcGU0UDzsxNoIrNl0kNl02LnwtLm4RERFd2oll9I1g5Itd3Ylk8o1j7Y1i6Ith4otf4Ipn
        +I9i64xWzYk/hnlr/5Jo/pBh5oxc4oxZ24pYxIpa2IlNt4RElnxl75BPmI1ayYtf3YlX0YdKt4ZN
        mYZRv4RTsoRSsoRYxYNGnn1HjH1Eg30IdmMLAAAANHRSTlMAsP7++/Lqpp+Gg1pOPDsyLBsU+vn4
        9/Lx6+bc2tDPyby4uLWuramgm3p2dGVlZU9COg8MiJ27qwAAANNJREFUGNNVztWSwjAYhuGfssAu
        i68r7i6Reou72/1fCQ0Qhr5H3zyZTALg//sogq3gEbenQRtFdZ1IP2z5WixrPGCK8MB7Oc9dSFIp
        6ggRJo5WltGXqiAivjbO4gBGmbWsyO7AVc5UN4m4K1gjxgR8YJVYSkoKrPMk8CJvC21TAVvPZl9b
        Vdlqhrk9jXuaUAYIuAUvt8d9D289+RexM/j3cxv3RWUmE4QnhxK/axpE6s4pktvO2xufoyGiqqp3
        f4EXTjtHxpAa76G7z9Q83y5XPAQnVOYeWm83sqgAAAAASUVORK5CYII='''

    CallInPixmap = None
    CallInData = '''
        iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAMAAABhEH5lAAAA/1BMVEUAAAAnNlcrO18qMlMpPFU9
        gbQ6d604bp8tWpE0bqczYpYqOFwmM1M3OU41TXoiJT4WFCUgJkAzL2Q3da5Ag7YwXpI3b6E2bZ02
        W4s4ZJU4ZpcuUHk4XI4mNlcyU4M3R2onNlczUn4ySG0uRHMvSW8uSXQiJ0MoN1kjM1EsOl4gHzkY
        EyU1PGguOk0jM1URERFJvP9LyP9Kw/9Nzf9Lxv9Kv/9O0v9N0P9Mzv9Fvv9DuP9BsP1Q3/9P1/9N
        yv9Kwf9Hwf9Fu/9Huv9HrO07nOZEnNU3g8Q/hbo0dbRLwPlDr/U/o+xHqeo5nOpHquI4ic1FicdC
        icI1eLQ3d7M5dqnvlSN2AAAAL3RSTlMAsJ46Fv39+fjy6YaDWk48MiwN+/Lx6unc2tDPyby4uLWu
        rampo3l2dGVlZU9CHXaW39gAAADVSURBVBjTVc3VjsMwEIXh0zTF7ZaWmRk8djgp8/IW3v9Z6lSd
        SvkvRppPsgeoHO8+IlE16zX+qwk6lVK1Dnm7FHpkfer53yWgrJeUONNzRzpEzbEJEUsKumLQJmXl
        6hAsuPmy2/Z+GhDGWpCedKz+AzQJg49c/MiPq5jiyisy85E7fEGi7UnXnb5CVzfZtkaBO37W3x5k
        SmzGX+ANb+9zVvP3pMI2Cn2nbyvyrMwTv51FnZYiIrux2NzYG4Q9chypjsC9X88HUdj9zNdYdG93
        xULhvIYlHygcH2ph8KcAAAAASUVORK5CYII='''

    CallFailedPixmap = None
    CallFailedData = '''
        iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAMAAABhEH5lAAABDlBMVEUAAAAmL2ZBhHY/fXc9eHU2
        ZHA+eXQnN1gnN1gnNlYwR2svS2orOWcoNWglMVoeIFATDzceI04yLnZJlIBCh3gvYnVKkoQ5a3I5
        bnM6YHk8a3w9bngyVWc7YXw0Vng3SGY1VXUfJFEmM2YiMVUrOGUcGU0UDzszM182Nl8xNoIrNl0f
        LmgrNWgdMGkpPGPZERFd2onomJFl9Y1e3Ylk841i64xh5Yxi54th4osRERFj7Y1d5Itg4IpWzYlM
        t4T/19Zr/5Jo/pBn+I9c3opZ24pYxIpa2IlSsoRJlYFElnw/h3lAhXhl75Bl8I1PmI1k7oxc4Yxa
        yYtW0IhNmYZRv4RYxYNGnn1HjH1Eg32hKSmGSrbTAAAAL3RSTlMAO/329vTq6bCwq6afhoM8MiwN
        +/v48uvm3NrQz8m4uK56dnRlZWVdWE9CHRkVFDTFbboAAADdSURBVBjTVY7lkgIxEISD2x12grvr
        ZpN1w90d3v9FCAupgv4x0/XVTM8AEEj8FwAV8yjBK9ddBz9QiucFJfYiLMOS+oswRCM/cR3mKWBV
        NAx707Y5dDOnIgMJCpw9TKxHZs0s71GUeKeFOLfsecZbFurqlCfGJbtJnnklYyhSlnTZBahaf/v+
        pAw+VJ0P0aH2cOEmZd8ztT8tkVjnj5+yr/MWTXw5G9cbJQOUzYactBMFiJaXIt2d6+pGxBiKXSvd
        rTiMMcSaxgtxQNXwLgx9PNAdobdn6r6ozZ4OgTuahB98PQrBvgAAAABJRU5ErkJggg=='''

    CallMissedPixmap = None
    CallMissedData = '''
        iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAMAAABhEH5lAAABF1BMVEUAAAA4dqwvR3AqMlM4bp/M
        EBAtWpE2bp8sO18qOFwmM1M3OU4iJT4WFCUgJkAoNlYmPFMzL2Q+hLNAg7Y1cao0bKQwXpIzYZQz
        ZJc2W4s4ZJU4ZpcuUHk4XI4yU4M3R2ozUn4uSXQiJ0MoN1kjM1EsOl4gHzkYEyU1PGguOk3RERFJ
        vP/qw8LomJHjLx/NERFLyP9Kw/9KwP9Nzf9Lxv/m5ub/19Y1drTfdmrLGhrZERHIERFO0v9N0P9M
        zv9DuP9BsP06nOhQ3/9Nyv9Hwf9Ev/9Fu/9Huv9EnNVDicX///9P1/9P1v9MxP9Hvf9LwPlDr/VI
        re1Gqu0/o+xHqepHquI4ic04g8Q3gsQ/hbw/hbg9frQ8d6yxgOaEAAAAKnRSTlMA/as6+fn46p+G
        g1o8MiwbFA378vLy8evm3NrQz8m4uK6jeXZ0ZWVlT0L5uI1FAAAA6UlEQVQY01WO1XLDQBRDZTvQ
        psEyM+6adu3EjtnhlJn//zs6bmc7jp7unNGVBFS3lo7xK1VzNRVA7TvsTWsZ6eiGZ+gdYMc0WX8j
        8+hdQkhXVyFFdBw9VwDNIG2/TQwNkskpvf5owvWIf+kTz8XaLaPMKrRyLvnJ5nZZyWcpzsB6PPpr
        LHrFrBF7qXm3P7MLzVISTM4wowVnFEzPs6vVEGz+fRh8ngJKebEi2NzrMJzIhwXr6mW7KthbHPEH
        m9HQ+joRv04y6N9QSu2e9N+xmsZjyrnJNiHUkJ00iUf3pXpuzMXB+vLKbh0/qYUmS4WmsSwAAAAA
        SUVORK5CYII='''

    WifiSignal0Pixmap = None
    WifiSignal0Data = '''
        iVBORw0KGgoAAAANSUhEUgAAACUAAAAPAgMAAAAex+7AAAAADFBMVEUAAADf39/ZERHa2tphOsv0
        AAAAAXRSTlMAQObYZgAAAFBJREFUCNdjgIFQBwwm0wKmpTDm6lNw5qpXMCbDqlVTIcz/B16tgmq7
        euDWChgTLAqWvnoApBYsdvUQ0AQYcyXQXKA0iLn0EJAJZIBhKDITAMjJOrW9TNAYAAAAAElFTkSu
        QmCC'''

    WifiSignal1Pixmap = None
    WifiSignal1Data = '''
        iVBORw0KGgoAAAANSUhEUgAAACUAAAAPBAMAAACRhxtgAAAAD1BMVEUAAADf39/a2traMiHlMiRE
        TMbOAAAAAXRSTlMAQObYZgAAADRJREFUGNNjQAdKSgoYYoqCeMQQ+tDFgHz8Ygh9EIxQg18MoQ+O
        oWoIixkbG2CImbgQJQYAZsMPo/Tq1Q8AAAAASUVORK5CYII='''

    WifiSignal2Pixmap = None
    WifiSignal2Data = '''
        iVBORw0KGgoAAAANSUhEUgAAACUAAAAPBAMAAACRhxtgAAAAD1BMVEUAAADf39/a2trZcB/gcCw6
        QFeFAAAAAXRSTlMAQObYZgAAADRJREFUGNNjQAdKSgoYYoqCeMQQ+tDFgHz8Ygh9EIxQQ1jM2NgA
        Q8zEhaAYSB+6GJBPlBgA18sRg3n5NH0AAAAASUVORK5CYII='''

    WifiSignal3Pixmap = None
    WifiSignal3Data = '''
        iVBORw0KGgoAAAANSUhEUgAAACUAAAAPBAMAAACRhxtgAAAAD1BMVEUAAADf39/a2tr23k721T3R
        dx7KAAAAAXRSTlMAQObYZgAAADRJREFUGNNjQAdKSgoYYoqCeMQQ+tDFgHzCYi4uDhhizsZ4xWD6
        0MWAfIJiIH3oYhA+YTEAR8oVzR2vvj8AAAAASUVORK5CYII='''

    WifiSignal4Pixmap = None
    WifiSignal4Data = '''
        iVBORw0KGgoAAAANSUhEUgAAACUAAAAPBAMAAACRhxtgAAAAD1BMVEUAAAC35Uip30nf39/a2trZ
        6zb+AAAAAXRSTlMAQObYZgAAADRJREFUGNNjQAcuLg4YYs7GhMWUlBQwxBQF8Ygh9KGLAfl4xWD6
        0MWAbIJiCH0IMSBNlBgAiOsUoXoH5kYAAAAASUVORK5CYII='''

    WifiSignal5Pixmap = None
    WifiSignal5Data = '''
        iVBORw0KGgoAAAANSUhEUgAAACUAAAAPAgMAAAAex+7AAAAACVBMVEUAAACC7kl36DUwSfEIAAAA
        AXRSTlMAQObYZgAAACxJREFUCNdjgIFVDXDmVGQmXBrOnIrKhErDmVPRmWBpOHMqJhMoDWdOxcYE
        AGqZMRs0hralAAAAAElFTkSuQmCC'''

    AddCirclePixmap = None
    AddCircleData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAA0lBMVEUAAABN2l4PxB4ApBMAdwkA
        cwcInhRZ42sR1CEuyEENryADiA0AqhUAlhAAkg8AXQIHrRsGpxkCdAgAmhEAjQ4AqhUAXQIAiQ0A
        XQIAqBQApRQAqRUAoRMbqiwXrihF0lcXwCcPvB9Ay1ErvTsjsDQRryEsvz0luTYTqCIDig8CiQ0R
        viI+xk8RpyLh4eH////o6Ojk5ORGz1cR0SIRyCLs7OzU1NRCy1M4wEkstT0TnyTc3NzX19dR2mJO
        1l8zu0QkrzUSmyMRtiIRtSIRtCL4+PiP7/pgAAAAK3RSTlMA9vZsTRrj/f3jzc3ExMTEv7+/p6em
        pmxsTU0aGv399vb29fX19ePj47+/GaKqWgAAALtJREFUGNNtytcSgjAURVEDgr0r3d5N6B2l4///
        kpdhfOM8JLPX3E7rZHozHm9o+d/ifIB6PTSYi01LQxQnhCQxGkp1KwtkWYGuB5a1XygA9M0nJNX1
        lBD/TgOsTkEYZq4W5Xl0WQFM/PCreZ+3ZhrRdgIwJZnXtKvupgDrc6WqqmbCU13XAPwDY1yaRgkf
        ywMwz4PjYMPFjnN8MR1Yd0TZdlHYNjXqQtayZKl+n2KX0M0YgZvNOAHuW/YDtm4XtkWWEkMAAAAA
        SUVORK5CYII='''

    DelCirclePixmap = None
    DelCircleData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAA0lBMVEUAAADEDw+nAAClAADpW1uo
        CAjRSUnORUXzaWm1JibjV1edCAixDw+IAwOWAACSAABdAACsBQV0AgKaAACNAACqAABdAACqAACe
        AACJAABdAAB/AABvAACFAABgAACsHR2vGBjcT0/BGBi8Dw/TR0fALi6vEhLQNzfPNjbGMjK9Kiqh
        CQmqFhanBweKAwOJAgK/ERGoERHYT0/KQkLSERHIERHu7u7jW1vd3d3R0dG/NzegFBTo6OjNzc3n
        X1+7MjKcEhK0ERH4+PiwJyemHBzIEhK9Qr1LAAAAMHRSTlMA9k0a9r/+/v369uPNzcTExMK/p6em
        pmxsbGxNTRoa/f329vb19fXj4+Pj4+K/v78oAQ+yAAAAn0lEQVQY023L1RaCUBRF0YuASXfbnRhI
        KGH8/y95hKtPzLe9xtioFqmroqjq5G836DnVblMLuoE3Q6VXkHaZspB094gNt9+XsWyesNbKgCBP
        4jjOnq8kz5OODIFrZo/wHoW3IEj6HAS+1YmqHfgDHoIyLXysmCkQzM3hb21CcHej96Uy3rsI2Cxx
        LhGsjUqO1CNg9iQHYZ6lCYJmeajOB7kGGLv2+7XfAAAAAElFTkSuQmCC'''

    ActiveCirclePixmap = None
    ActiveCircleData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAA51BMVEUAAABN2l4PxB4AlA8ApRQa
        qysInhRZ42sNryADiA0AqhUAXQIHrRsGpxkCdAgAmhEAjQ4AqhUAXQIAqhUAnhIAiQ0AXQIAqBQA
        pRQAfwsAbwcAhQwAYANF0lcXwCcPvB9Ay1ErvTsjsDQRryEvyEIux0Esvz0luTYTqCIDig8CiQ0R
        0iHn5+fj4+MRtCLe3t5GzldBylI9xU5O1l8RyCIRviI3v0gRriIRoiLV1dUxukIRqiIRpyIRnyL/
        ///4+Pjr6+ui16me4qdS2mNR2WJHz1gttT4rszwmrzccpC0VwCYVniYSyCNbA1xzAAAAK3RSTlMA
        9vbEGv7j/c3NxMS/v7+np6ambGxsbE1NTU0aGvb29vX19fXj4+Pj47+/AarJhwAAALFJREFUGNNt
        y9UWgkAUhWEGFTvpsFtgEIPGbn3/5/EwLu/47v69zqFSZdlmqdRks/8WKyOUz6NxRfy1VEDnNbig
        gkTuq+i6TDh2u5p8cRN7lQh2J3vKwVDvOTcneDxN03gP6jBk7Ps+58WWacReLkOGo3+IoL0wJEOj
        7/oWdIQxHjZg4GcvF9rdAoaHQZ13PtjAG9BdqBSQi7SOdUAXZYpQagwNydQUCEITWuVyS9CoNF+w
        UhgX3khsvgAAAABJRU5ErkJggg=='''

    InactiveCirclePixmap = None
    InactiveCircleData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAA21BMVEUAAADEDw9zAADpW1usICDz
        aWm1JibjV1edCAixDw+IAwOqAACWAACSAABdAACuCQmoBwd0AgKaAACNAACqAABdAACqAACeAACJ
        AABdAACoAAClAAB/AABvAACpAAChAACvGBjcT0/BGBi8Dw/TR0fALi6vEhLQNzfPNjbGMjK9Kiqh
        CQmqFhaKAwOJAgL////d3d2rERHSERG1ERHR0dHW1tbjW1vXT0+gEhKyERHu7u7RSEjLQkLq6urn
        5+fi4uLnX1+6MDDAExPIERGdERH39/fZUVHYUFC/NzeKi/ywAAAAL3RSTlMA9hr2/v369uPNzcTE
        xMS/v7+np6ambGxsbE1NTU0aGv329vb19fXj4+Pj4+K/v7D5oYgAAAC4SURBVBjTbY9HEoJAFAUF
        zDknkjnrMAwqWYLp/ifyURY7evGruutvXi4TZdiv1fpDJfVpaysUCsKuNf27WBGCGwhKFTFxtV16
        kzsgn3lbRRjtHUKI6+I4hxFCd/XNk5evadrTLHYR6k4YmoZxhZv5OkLDLVIKf1BKZw2E3pqxxH2P
        sU0PYXyK4JR6th0dxwj8eWFpVhxbtrW88DkgVTmmA8ZVJSiQO2VO17lyR07H8JNBszmY4D+DH5c8
        GZRRf1EmAAAAAElFTkSuQmCC'''

    LocChangePixmap = None
    LocChangeData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAvVBMVEUAAAAuh9IYarWVAADlAQHl
        AQHfAQGuAAD9hob8hIT8iYnwaGj2c3PlUlK9HBzyT0/eNTU4lN8NXKfMIyPxSkqfAADFAgKyAADi
        AQHVAQHNAQGVAAC8AQEyjNcKV6PlAQHFAQHlAQE3ZaNIQ3JZVIMjecM+nOcGUZw+nOcZbLeMIzaq
        AAD6bW3+dXX1YmJd0f/4aWnwWFiV5P9u1///gYH6dHT8cXGoY2ObVVVXS0s4xf//kJBhVlZISEhK
        Pz/xJFURAAAALHRSTlMAzczKn3KqC/3z8vHt7dDPzczMzMvHsa+jn2dmYVxcGRQT9OrozJmZXFxa
        Wv2CKdQAAAChSURBVBjTPczXDsIwDEDRQAd0711oyx5J92T9/2cRJNz7YMlHltGvjGN5lssQlLC2
        +BRtNgHgtJYQ0mocgC+Q4TUQwQfg1/30nvo1DxDIePyMWA4AQr3DGHd6CJC6UlmWkpsiKLZwjq0Y
        za08JVe8FTpdQO5qrt4QMowNnDj5YUGrFyBOtauboiia4x+Yar+kPZbXGRg6TXMLXyMmovNM9y89
        NA8T2JpwAgAAAABJRU5ErkJggg=='''

    ExcelDocPixmap = None
    ExcelDocData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAApVBMVEUAAAALKipVf38yV1clSUk+
        ZWVIcXFSfHxTfX0XODgMLCyHqmVJiidVf3/////8/v35/PyHqmVIiib2+/vx9/ft9fXi8/P0+fno
        +OjV5uZ6o1hyn1Bflj3s++xpmkdWkTTn8fHf7OzZ6OjO4MaTpKSewo36/v7v+fn4/fjq9/f0/PTl
        9PTv+u/Y5c+auoOCp2BOjSyxwsLH3b+ltraTtnqCrWhzplviWV3bAAAADnRSTlMAh2Z2e3FsZySC
        ZcDATY/2reYAAACkSURBVBjTPchXFoIwAETRKCiCGlASEBIIIL1b9780U4Q358zHBQCct/8OQGW4
        VdN5nvcwpBwvqjF4QSkTVE1Bnuc6h9AOw2HknwWBt+dAajIQ8q5JmimI23vM18ZJmkmg/YfSJ+0p
        TtJux4FFRVEwFjGMk0bAHN1E0YwwrgScrqovQtjXgEiDtu04ro/QCou4CnS4iKtLMKEUu3RKU4K1
        WbMA+AEaBhF5P7HRSAAAAABJRU5ErkJggg=='''

    MailSendPixmap = None
    MailSendData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAABAlBMVEUAAABUf382XFxFbGxNdnYY
        arUNXKcvVFQ+ZWUTZK9Vf39bzvtYx/JUvucic7ZOsthIpcZAlLIYarU3gpooZowtboAYarUGUZwi
        WWUYREsYarUQMjMfQkIYarUZbLcGUZwPMDAYarUYarUYarUYarX////7/f33/Pzu9vba6enc5eXz
        +Pji7u7s8fHo8fHl7Oze6+vh6end6elWot3I2dnB0tJd0f/z+vrv+fno9vbp7++ey+jW4eFysuDS
        3t7N29u4ycm0xcWvwMCqu7ultrahsrKdrq6Z5f+A3f9OzP/M5u+/3e2hz+3S5+yv1eqOweTU4+N/
        uOFjp9xSndlLldG8zs5E3CI9AAAAJXRSTlMAZ3RuasrMeHFjTfry5+DbzcC1srKlo5mZkI6Ifnhm
        ZmRKNCAQ/OaO6QAAALtJREFUGNNlz9XSglAABOClrD/tbgU8HhBF7O5u3/9VRIdxhvG72N3bxQcP
        Y+MBM1KKb8qIAa+MO6KlM1Z48GJlUpFezCHy4KRydVotm54lceCaskxmxIomB1dLVakx7/XmBlXV
        lgusTGv12mCxGJhFZRZsm9SJpg2Hmkb63TYLJzVOJYuu75xI3Peb7aF7PPcv+nV5CyATj0aCfu//
        38/3V6Ox+gVQyOey7mQs5BOEtZCyHXU43LAJp4EH6Ikfv0pcilsAAAAASUVORK5CYII='''

    GreenLightPixmap = None
    GreenLightData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAe1BMVEUAAABApkAVexUVfBVHrUdA
        pkAfhR8YfhhEqkQymDIjiSMRdxFEqkQ2nDYfhR8RdxFEqkQ7oTt33Xd84nxVu1VSuVJEqkQ6oTqG
        7IaB54FHrUczmTNu1W5nzmdPtU9Ns01KsUoulS5y2HJhx2FexF48ojwojigjiSMRdxHv6MSoAAAA
        EnRSTlMAZWUq5+fn587Ozs6CgoKCKipZck9nAAAAjUlEQVQY023LVw7EIAxFUdJ7HZtkGGAgff8r
        jIVQvnK+/K5k9qqvc87zumdeEK/jPI9rHPhtltlZjCtDIr+eTAYKDXwe0FAo1PhQBQWLAjclpdro
        sBQOPf28SR8UShCTJ6Ck0O4ouCNwbylEqUH9JxpNGjESngIAEUCcIXPCzHIAbjO/6aurrqvqIvbm
        Bn4GDkNe+slZAAAAAElFTkSuQmCC'''

    BlueLightPixmap = None
    BlueLightData = '''
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAclBMVEUAAABilcg3ap5om85hlMc/
        cqU4a55mmcxUh7pFeKszZplmmcxYi75BdKczZpk5bJ81aJtmmcxdkMOHuu1LfrGNwPNjlslDd6qX
        yv2SxfhmmcxZjL9Vibxgk8ZdkMR7r+JvotVqntGAs+Z5rN9PgrUzZpmGNHqIAAAAE3RSTlMAZSrn
        5+fnzs7OzoKCgoJlZSoq8f8qLgAAAIpJREFUGNNtyEkShSAMRVHEvm/A6E9UwGb/W/wpinLkmeTl
        ik9jnSPm9SiCKDbzus4mjsLv1Oop58uUqF+gkolDY+eXbTgURr1MweEGAnud52V53Bz0rpeAJ4fS
        kQ7IlRzaDWjzCLaWg0x32A/GJ5WC9cuBCIB4LL3whkwTIulsEIHsquepOim+/AF2/A5LptNA+AAA
        AABJRU5ErkJggg=='''


    ### Load all icons from base64 data
    @staticmethod
    def load():
        LmIcon.AppIconPixmap = QtGui.QPixmap()
        LmIcon.AppIconPixmap.loadFromData(base64.b64decode(LmIcon.AppIconData))

        LmIcon.TickPixmap = QtGui.QPixmap()
        LmIcon.TickPixmap.loadFromData(base64.b64decode(LmIcon.TickData))

        LmIcon.CrossPixmap = QtGui.QPixmap()
        LmIcon.CrossPixmap.loadFromData(base64.b64decode(LmIcon.CrossData))

        LmIcon.DenyPixmap = QtGui.QPixmap()
        LmIcon.DenyPixmap.loadFromData(base64.b64decode(LmIcon.DenyData))

        LmIcon.NotifPixmap = QtGui.QPixmap()
        LmIcon.NotifPixmap.loadFromData(base64.b64decode(LmIcon.NotifData))

        LmIcon.CallOutPixmap = QtGui.QPixmap()
        LmIcon.CallOutPixmap.loadFromData(base64.b64decode(LmIcon.CallOutData))

        LmIcon.CallInPixmap = QtGui.QPixmap()
        LmIcon.CallInPixmap.loadFromData(base64.b64decode(LmIcon.CallInData))

        LmIcon.CallFailedPixmap = QtGui.QPixmap()
        LmIcon.CallFailedPixmap.loadFromData(base64.b64decode(LmIcon.CallFailedData))

        LmIcon.CallMissedPixmap = QtGui.QPixmap()
        LmIcon.CallMissedPixmap.loadFromData(base64.b64decode(LmIcon.CallMissedData))

        LmIcon.WifiSignal0Pixmap = QtGui.QPixmap()
        LmIcon.WifiSignal0Pixmap.loadFromData(base64.b64decode(LmIcon.WifiSignal0Data))

        LmIcon.WifiSignal1Pixmap = QtGui.QPixmap()
        LmIcon.WifiSignal1Pixmap.loadFromData(base64.b64decode(LmIcon.WifiSignal1Data))

        LmIcon.WifiSignal2Pixmap = QtGui.QPixmap()
        LmIcon.WifiSignal2Pixmap.loadFromData(base64.b64decode(LmIcon.WifiSignal2Data))

        LmIcon.WifiSignal3Pixmap = QtGui.QPixmap()
        LmIcon.WifiSignal3Pixmap.loadFromData(base64.b64decode(LmIcon.WifiSignal3Data))

        LmIcon.WifiSignal4Pixmap = QtGui.QPixmap()
        LmIcon.WifiSignal4Pixmap.loadFromData(base64.b64decode(LmIcon.WifiSignal4Data))

        LmIcon.WifiSignal5Pixmap = QtGui.QPixmap()
        LmIcon.WifiSignal5Pixmap.loadFromData(base64.b64decode(LmIcon.WifiSignal5Data))

        LmIcon.AddCirclePixmap = QtGui.QPixmap()
        LmIcon.AddCirclePixmap.loadFromData(base64.b64decode(LmIcon.AddCircleData))

        LmIcon.DelCirclePixmap = QtGui.QPixmap()
        LmIcon.DelCirclePixmap.loadFromData(base64.b64decode(LmIcon.DelCircleData))

        LmIcon.ActiveCirclePixmap = QtGui.QPixmap()
        LmIcon.ActiveCirclePixmap.loadFromData(base64.b64decode(LmIcon.ActiveCircleData))

        LmIcon.InactiveCirclePixmap = QtGui.QPixmap()
        LmIcon.InactiveCirclePixmap.loadFromData(base64.b64decode(LmIcon.InactiveCircleData))

        LmIcon.LocChangePixmap = QtGui.QPixmap()
        LmIcon.LocChangePixmap.loadFromData(base64.b64decode(LmIcon.LocChangeData))

        LmIcon.ExcelDocPixmap = QtGui.QPixmap()
        LmIcon.ExcelDocPixmap.loadFromData(base64.b64decode(LmIcon.ExcelDocData))

        LmIcon.MailSendPixmap = QtGui.QPixmap()
        LmIcon.MailSendPixmap.loadFromData(base64.b64decode(LmIcon.MailSendData))

        LmIcon.GreenLightPixmap = QtGui.QPixmap()
        LmIcon.GreenLightPixmap.loadFromData(base64.b64decode(LmIcon.GreenLightData))

        LmIcon.BlueLightPixmap = QtGui.QPixmap()
        LmIcon.BlueLightPixmap.loadFromData(base64.b64decode(LmIcon.BlueLightData))

