// from http://code.google.com/p/django-voting/wiki/RedditStyleVoting

//VoteHijacker = function(prefix) {
//}

var VoteHijacker = Class.create();
VoteHijacker.prototype =
{
    initialize: function(prefix)
    {
        this.prefix = prefix || "";
        this.registerEventHandlers();
    },

    registerEventHandlers: function()
    {
        $$("form." + this.prefix + "_vote").each(function(form)
        {
            Event.observe(form, "submit", this.doVote.bindAsEventListener(this), false);
        }.bind(this));
    },

    doVote: function(e)
    {
        Event.stop(e);
        var form = Event.element(e);
        var id = /(\d+)_/.exec(form.id)[1];
        var action = /(up|down|clear)vote/.exec(form.action)[1];
        new Ajax.Request(form.action, {
            onComplete: VoteHijacker.processVoteResponse(this.prefix, id, action)
        });
    }
};

VoteHijacker.processVoteResponse = function(prefix, id, action)
{
    return function(transport)
    {
        var response = transport.responseText.evalJSON();
        if (response.success === true)
        {
            var upArrowType = "grey";
            var upFormAction = "up";
            var downArrowType = "grey";
            var downFormAction = "down";

            if (action == "up")
            {
                var upArrowType = "mod";
                var upFormAction = "clear";
            }
            else if (action == "down")
            {
                var downArrowType = "mod";
                var downFormAction = "clear";
            }

            VoteHijacker.updateArrow("up", prefix, id, upArrowType);
            VoteHijacker.updateArrow("down", prefix, id, downArrowType);
            VoteHijacker.updateFormAction("up", prefix, id, upFormAction);
            VoteHijacker.updateFormAction("down", prefix, id, downFormAction);
            VoteHijacker.updateScore(prefix, id, response.score);
        }
        else
        {
            alert("Error voting: " + response.error_message);
        }
    };
};

VoteHijacker.updateArrow = function(arrowType, prefix, id, state)
{
    var img = $(prefix + "_" + id + "_" + arrowType + "_arrow");
    var re = new RegExp(arrowType + "_(?:mod|grey)\\.png");
    img.src = img.src.replace(re, arrowType + "_" + state + ".png");
};

VoteHijacker.updateFormAction = function(formType, prefix, id, action)
{
    var form = $(prefix + '_' + id + '_' + formType);
    form.action = form.action.replace(/(?:up|down|clear)vote/, action + "vote");
};

VoteHijacker.updateScore = function(prefix, id, score)
{
    var scoreElement = $(prefix + "_" + id + "_score");
    scoreElement.innerHTML = score.score;
    scoreElement.title = "after " + score.num_votes + " vote" + VoteHijacker.pluralize(score.num_votes);
};

VoteHijacker.pluralize = function(value)
{
    if (value != 1)
    {
        return "s";
    }
    return "";
};
