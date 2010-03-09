var isIE6 = navigator.userAgent.toLowerCase().indexOf('msie 6') != -1;
$(window).load(function(){
    $('.QuestionDisplay img').each(function(){
        if (this.width > 520) 
            $(this).css('width', '520px');
    });
    var LocationHash = window.location.hash;
    if(LocationHash){
	    var SelectedClass = LocationHash.replace('#', '');
	    if ($('.' + SelectedClass).length > 0) {
	        $('.' + SelectedClass).animate({
	            backgroundColor: "#F2E291"
	        }, 500).animate({
	            backgroundColor: "#FFF"
	        }, 2000);
	    }
    }
});
$(function(){
    if (!isIE6) {
        $("#SolutionTextWysiwyg").wysiwyg();
    }
    $(".SubmitReport").click(function(){
        var ReasonsArray = new Array;
        var FormID = $(this).parents('.ReportAbuse:first').attr('id');
        $(this).parents('.ReportAbuseForm:first').find("input[name='Reason']:checked").each(function(){
            ReasonsArray.push('\'' + $(this).val() + '\'')
        });
        var _XSRF = $(this).parents('.ReportAbuseForm:first').find("input[name='_xsrf']").val()
        var Reasons = '[' + ReasonsArray.join(',') + ']';
        var Explanation = $(this).parents('.ReportAbuseForm:first').find("textarea[name='Explanation']").val()
        var ProblemID = $(this).parents('.ReportAbuseForm:first').find("input[name='ProblemID']").val()
        var QuestionIndex = $(this).parents('.ReportAbuseForm:first').find("input[name='QuestionIndex']").val()
        $.post('/prep/report_abuse/', {
            _xsrf: _XSRF,
            reason_options: Reasons,
            explanation: Explanation,
            problem_id: ProblemID,
            question_index: QuestionIndex
        }, function(data){
            if (data == "Success") {
                $("#" + FormID).find('.ReportFormBody').html("<div class=\"ReportMessageDiv\">Report Submitted successfully</div>");
            }
            else 
                if (data != "Success") {
                    if ($("#" + FormID).find('.ReportErrorDiv').length > 0) 
                        $("#" + FormID).find('.ReportErrorDiv').html(data);
                    else 
                        $("#" + FormID).find('.ReportFormBody').prepend('<div class="ReportErrorDiv">' + data + '</div>');
                }
            var width = $("#" + FormID).find('.ReportAbuseForm').width();
            var height = $("#" + FormID).find('.ReportAbuseForm').height();
            var selfTop = $("#" + FormID).find('.ReportButton').position().top;
            var selfLeft = $("#" + FormID).find('.ReportButton').position().left;
            var selfWidth = $("#" + FormID).find('.ReportButton').width();
            var posTop = selfTop - height;
            var posLeft = selfLeft - width + selfWidth + parseInt($("#" + FormID).find('.ReportButton').css("padding-left").replace(/px/g, '')) + parseInt($("#" + FormID).find('.ReportButton').css("padding-right").replace(/px/g, ''));
            $("#" + FormID).find('.ReportAbuseForm').css({
                top: posTop + "px",
                left: posLeft + "px"
            });
        });
    });
    $(".CloseReport").click(function(){
        $(this).parents('.ReportAbuseForm:first').fadeOut('fast');
        $(this).parents('.ReportAbuseForm:first').prev('.ReportButton').removeClass('ReportButtonClicked');
    });
    $('.ReportButton').click(function(){
        var width = $(this).parent().find('.ReportAbuseForm').width();
        var height = $(this).parent().find('.ReportAbuseForm').height();
        var selfTop = $(this).position().top;
        var selfLeft = $(this).position().left;
        var selfWidth = $(this).width();
        var posTop = selfTop - height;
        var posLeft = selfLeft - width + selfWidth + parseInt($(this).css("padding-left").replace(/px/g, '')) + parseInt($(this).css("padding-right").replace(/px/g, ''));
        $(this).parent().find('.ReportAbuseForm').fadeIn('fast');
        $(this).parent().find('.ReportAbuseForm').css({
            top: posTop + "px",
            left: posLeft + "px"
        });
        $(this).addClass('ReportButtonClicked');
    })
    $(".AddAComment form").submit(function(){
        if ($(this).find("textarea").val() == '') {
            $(this).prepend('<div class="ReportErrorDiv">' + "<ul><li>Cannot post a blank comment</li></ul>" + '</div>');
            return false;
        }
    });
    $(document).bind('click', function(e){
        var $clicked = $(e.target);
        if ($clicked.isChildOf('.ReportAbuse')) {
        }
        else {
            $('.ReportAbuseForm').fadeOut('fast');
            $('.ReportAbuseForm').prev('.ReportButton').removeClass('ReportButtonClicked');
        }
    });
    $("#SubmitAnswerForm").submit(function(){
        if ($("input[name='option']:checked").length < 1) {
            if ($('.FormErrors').length < 1) {
                $(this).parent().prepend('<div class="FormErrors" style="display: none;">Please select an answer for this question and submit again</div>');
                $('.FormErrors').fadeIn("fast");
            }
            else {
                $('.FormErrors').fadeOut("fast", function(){
                    $(this).fadeIn("fast")
                });
            }
            return false;
        }
    });
    if($('.AddACommentLink').length>0){
    	$('.AddACommentLink').click(function(){
    		$(this).parents('.SolutionBody').find('.AddAComment').slideDown();
    	});
    }
    var TGIndex = '';
    if($('.TGLink').length>0){
    	$('.TGLink').each(function(i){
    		$(this).click(function(){
    			$('.TGLink').removeClass('TGLinkActive');
    			if (i == TGIndex){
    				$('.TGLink').addClass('TGLinkActive');
    				TGIndex = i;
    			}
        		$('.TGList').hide();
        		$('.TGList').eq(i).show();
        	});
    	})
    }
    if ($(".Comment").length > 3) {
        $(".Comment").hide();
        $(".first_comment").show();
        $(".second_comment").show();
        $(".last_comment").show();
		var Comments = new Array();
		$('.SolutionContent').each(function(){
			 Comments.push($(this).find(".Comment").length - 3);
		});
		var i = 0;
		$(".second_comment").each(function(){
			$(this).after('<a href="javascript:void(0)" class="ShowAllComments">Show '+(Comments[i])+' more comments</a>');
			i++;
		});
		$('.ShowAllComments').click(function(){
			$(this).parents(".SolutionContent:first").find(".Comment").show();
			$(this).remove();
		});
    }
    $('.FavoriteInActive,.FavoriteActive').click(function(){
    	$(this).parents('form:first').submit();
    	return false;
    });
});
