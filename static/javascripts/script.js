$(function(){
    $('#add_option').click(function(){
        var OptionVal = $('#OptionFields .InputTextArea').size();
        if (OptionVal < 9) {
            $('#OptionFields').append('<tr><td>' + String.fromCharCode(OptionVal + 97) + ')</td><td><textarea name="option_descriptions" id="option_descriptions_' + OptionVal + '" class="InputTextArea"></textarea></td><td align="center"><input type="radio" name="option_answers" id="option_answers_' + OptionVal + '" value="' + OptionVal + '" /></td></tr>');
            $('#OptionFields .InputTextArea:last').each(function(){
                $(this).after('<div class="MakeRichText"><A href="javascript:void(0)">Make RichText</a></div><div class="RemoveRichText" style="display:none;"><A href="javascript:void(0)">Remove RichText</a></div>');
            });
            AddRichTextActions();
            SelectRadio();
        }
        else 
            alert("Maximum 8 options are accepted!");
    });
    $('#remove_option').click(function(){
        var OptionVal = $('#OptionFields .InputTextArea').size();
        if (OptionVal > 4) 
            $('#OptionFields tr:last-child').remove();
        else 
            alert("Minimum 4 options are needed!");
    });
    $('#add_option_for_edit').click(function(){
        var OptionVal = $('#OptionFields .Text').size();
        if (OptionVal < 9){
            $('#OptionFields').append('<tr><td>' + String.fromCharCode(OptionVal + 97) + ')</td><td><input type="text" name="option_descriptions" id="option_descriptions_' + OptionVal + '" class="Text" /></td><td align="center"><input type="radio" name="option_answers" id="option_answers_' + OptionVal + '" value="v' + OptionVal + '" /></td></tr>');
            SelectRadio();
        }
        else 
            alert("Maximum 8 options are accepted!");
    });
    $('#remove_option_for_edit').click(function(){
        var OptionVal = $('#OptionFields .Text').size();
        if (OptionVal > 4) 
            $('#OptionFields tr:last-child').remove();
        else 
            alert("Minimum 4 options are needed!");
    });
    $('a[target="UploadFrame"]').bind('click keypress', function(){
        var MapsURL = $(this).prev().val();
        var URL = $(this).attr('href');
        OpenPopUp(URL, 500, 400, 'center', 'yes', "UploadFrame");
    });
    function RichTextForOptions(){
        if ($('#OptionFields .InputTextArea').length > 0) {
            $('#OptionFields .InputTextArea').each(function(){
                $(this).after('<div class="MakeRichText"><A href="javascript:void(0)">Make RichText</a></div><div class="RemoveRichText" style="display:none;"><A href="javascript:void(0)">Remove RichText</a></div>');
            })
            AddRichTextActions();
            $("#OptionFields .InputTextArea").each(function(){
                var InputValue = $(this).val();
                if (InputValue.match('<[a-zA-Z0-9+].*?>|</[a-zA-Z0-9+]>')) {
                    $(this).wysiwyg();
                    $(this).parents("td:first").find(".MakeRichText").hide();
                    $(this).parents("td:first").find(".RemoveRichText").show();
                }
            });
        }
    }
    function AddRichTextActions(){
        if ($('#OptionFields .InputTextArea').length > 0) {
            $('.MakeRichText a').click(function(){
                $(this).parents(".MakeRichText:first").prev().wysiwyg({
                    controls: {
                        insertOrderedList: {
                            visible: false
                        },
                        insertUnorderedList: {
                            visible: false
                        },
                        createLink: {
                            visible: false
                        },
                        separator04: {
                            visible: false
                        },
                        separator05: {
                            visible: false
                        },
                        separator06: {
                            visible: false
                        },
                        separator07: {
                            visible: false
                        },
                        separator08: {
                            visible: false
                        },
                        increaseFontSize: {
                            visible: false
                        },
                        decreaseFontSize: {
                            visible: false
                        },
                        h1mozilla: {
                            visible: false
                        },
                        h2mozilla: {
                            visible: false
                        },
                        h3mozilla: {
                            visible: false
                        },
                        h1: {
                            visible: false
                        },
                        h2: {
                            visible: false
                        },
                        h3: {
                            visible: false
                        }
                    }
                });
                $(this).parent().hide();
                $(this).parents("td:first").find('.RemoveRichText').show();
            });
            $('.RemoveRichText a').click(function(){
                $(this).parents("td:first").find('.wysiwyg').remove();
                var InputText = $(this).parents("td:first").find("textarea").val();
                $(this).parents("td:first").find("textarea").val(InputText.replace(/<(?:.|\s)*?>/g, ""));
                $(this).parents("td:first").find("textarea").show();
                $(this).parent().hide();
                $(this).parents("td:first").find('.MakeRichText').show();
            });
        }
    }
    RichTextForOptions();
    if($("#IAgree").length>0){
      $(".QuestionForm form").submit(function(){
        if($("#IAgree").is(':checked')) return true;
        else {
          $("#IAgree").parents('.IAgreeDiv').css("background-color", '#FFFFCC');
          $("#IAgree").parents('.IAgreeDiv').css("border-color", '#CC0000');
          $("#IAgree").parents('label:first').css("color", '#CC0000');
          alert("You must agree to the COPYRIGHT POLICY");
          return false;
        }
      });
      $("#IAgree").click(function(){
        if($(this).is(':checked')){
          $(this).parents('.IAgreeDiv').css("background-color", '#F0FFF0');
          $(this).parents('.IAgreeDiv').css("border-color", '#00FF00');
          $(this).parents('label:first').css("color", '');
        }else {
          $(this).parents('.IAgreeDiv').css("background-color", '');
          $(this).parents('.IAgreeDiv').css("border-color", '');
          $(this).parents('label:first').css("color", '');
        }
      });
    }
    SelectRadio();
});
function OpenPopUp(url, mwidth, mheight, position, scroll, popupname){
    var url = (url == null) ? '' : url;
    var position = (position == null) ? 'center' : position;
    var scroll = (scroll == null) ? 'yes' : scroll;
    var popupname = (popupname == null) ? 'PopUp' : popupname;
    
    var winl = (screen.width - mwidth) / 2;
    var wint = (screen.height - mheight) / 2;
    var settings = 'height=' + mheight + ',';
    settings += 'width=' + mwidth + ',';
    switch (position) {
        case 'top-center':
            settings += 'top=' + 0 + ',';
            settings += 'left=' + winl + ',';
            break;
        case 'center':
            settings += 'top=' + wint + ',';
            settings += 'left=' + winl + ',';
            break;
        case 'bottom-center':
            settings += 'top=' + (screen.height - mheight) + ',';
            settings += 'left=' + winl + ',';
            break;
        case 'top-left':
            settings += 'top=' + 0 + ',';
            settings += 'left=' + 0 + ',';
            break;
        case 'top-right':
            settings += 'top=' + 0 + ',';
            settings += 'left=' + (screen.width - mwidth) + ',';
            break;
        case 'center-left':
            settings += 'top=' + wint + ',';
            settings += 'left=' + 0 + ',';
            break;
        case 'center-right':
            settings += 'top=' + wint + ',';
            settings += 'left=' + (screen.width - mwidth) + ',';
            break;
        case 'bottom-left':
            settings += 'top=' + (screen.height - mheight) + ',';
            settings += 'left=' + 0 + ',';
            break;
        case 'bottom-right':
            settings += 'top=' + (screen.height - mheight) + ',';
            settings += 'left=' + (screen.width - mwidth) + ',';
            break;
        default:
            settings += 'top=' + wint + ',';
            settings += 'left=' + winl + ',';
            break;
    }
    settings += 'scrollbars=' + scroll + ',';
    settings += 'resizable=0';
    win = window.open(url, popupname, settings);
    if (parseInt(navigator.appVersion) >= 4) {
        win.window.focus();
    }
}

function SelectRadio(){
    if($("#OptionFields").length > 0){
      $("#OptionFields input[type=radio]").click(function(){
        $("#OptionFields tr").css("background","#FFF");
        $(this).parents("tr:first").css("background","#fff8bf");
      });
    }
}

function InsertContentIntoW(id, content){
    if ($("#" + id + "IFrame").length > 0) {
        $("#" + id + "IFrame").contents().find('body').append(content);
    }
}
