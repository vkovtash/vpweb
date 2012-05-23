<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <title>ViPaper</title>
    <link rel="stylesheet"  href="//code.jquery.com/mobile/1.1.0/jquery.mobile-1.1.0.min.css" />
    <script src="//code.jquery.com/jquery-1.7.1.min.js"></script>
    <script src="//code.jquery.com/mobile/1.1.0/jquery.mobile-1.1.0.min.js"></script>

    <script src="http://malsup.github.com/jquery.form.js"></script>

    <style type="text/css">
        .episode {
            font-family: Helvetica, Arial, sans-serif;
        }

        .episode .title{
            float: left;
            padding: 15px;
            vertical-align: middle;
            display: table-cell;
            width: 100px;
        }

        .episode .title p {
            font-size: 16px;
            font-weight: bold;
            margin: 0px;
        }

        .downloadedControl{
            position: relative;
            top: -10px;
            vertical-align: middle;
            display: table-cell;
        }
        .downloadedControl p{
            font-size: 12px;
            margin: 0px;
            position: relative;
            left: 5px;
            padding: 0px;
        }
    </style>
</head>
<body>
<div data-role="page">
    <div data-role="content">
    <ul data-role="listview">{% for show in Shows %}
        <li>
        <h3>{{show.title}}</h3>
        <p>Season {{show.season}}</p>
        <img src="{{ show.posterURL }}">

        <p class="ui-li-count">{{ show.episodes|length }}</p>
        <ul>{% for episode in show.episodes %}
                <ol>
                <div class="episode" data-role="fieldcontain">
                    <div class="title">
                        <p>Episode {{episode.number}}</p>
                    </div>
                    <div class="downloadedControl">
                    <p class="label">Downloaded</p>
                    <form id="fsh{{ forloop.parentloop.counter }}ep{{ forloop.counter }}" action="/setdownloaded" method="get">
                    <input type="hidden" value="{{ show.showKey }}" name="show_key">
                    <input type="hidden" value="{{ episode.number }}" name="ep_num">
                    <select id="dlsh{{ forloop.parentloop.counter }}ep{{ forloop.counter }}" name="is_downloaded" id="flip-c"
                            data-role="slider" data-theme="a"
                            data-mini="true"
                            onchange="$('#fsh{{ forloop.parentloop.counter }}ep{{ forloop.counter }}').ajaxSubmit({error:function() {$('#dlsh{{ forloop.parentloop.counter }}ep{{ forloop.counter }}').val('{{ episode.isDownloaded }}').slider('refresh');}});">
                        {% if episode.isDownloaded == '1' %}
                            <option value="0">No</option>
                            <option value="1" selected="selected">Yes</option>
                        {% else %}
                            <option value="0" selected="selected">No</option>
                            <option value="1" >Yes</option>
                        {% endif %}
                    </select>
                    </form>
                    </div>
                </div>
                </ol>
            {% endfor %}
            </ul>
            </li>
    {% endfor %}</ul>
    </div><!-- /content -->
    </div><!-- /page -->
</body>
</html>