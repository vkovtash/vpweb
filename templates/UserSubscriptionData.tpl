<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <title>ViPaper</title>
</head>
<body>
    {% for show in Shows %}
        <div>{{show.title}}{{show.season}}
        <div>
            {% for episode in show.episodes %}
                <div>{{episode.number}}
                {% if episode.isDownloaded == '1' %}
                <a href="/setdownloaded?is_downloaded=0&ep_num={{ episode.number }}&show_key={{ show.showKey }}">Downloaded</a>
                {% else %}
                    <a href="/setdownloaded?ep_num={{ episode.number }}&show_key={{ show.showKey }}">Not Downloaded</a>
                {% endif %}
                </div>
            {% endfor %}
        </div>
        <div>
    {% endfor %}
</body>
</html>