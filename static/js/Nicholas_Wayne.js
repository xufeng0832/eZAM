/**
 * Created by xuchao on 2017/3/9.
 */
(function (nw) {
     /*
    用于保存当前作用域内的"全局变量"
     */
    var NB_GLOBAL_DICT = {};

    /*
    用于向后台发送请求的url
     */
    var requestUrl;



    // 聚合搜索条件
    function aggregationSearchCondition(){
        var ret = {};
        $("#search_conditions").children().each(function(){
            var $condition = $(this).find("input[is-condition='true'],select[is-condition='true']");
            var name = $condition.attr('name');
            var value = $condition.val();
            if (!$condition.is('select')) {
                name = name + "__contains";
            }
            if (value){
                var valList = $condition.val().trim().replace(',',',').split(',')
                if (ret[name]){
                    ret[name] = ret[name].concat(valList);
                }else {
                    ret[name] = valList;
                }
            }
            //console.log(!$condition.is('select'))
        });
        //console.log(ret)
        return ret
    }


    // 页面初始化 (获取数据,绑定事件)
    function initialize(pager){
        //$.Show('#shade,#loading');
        var conditions = JSON.stringify(aggregationSearchCondition());
        //console.log(conditions)
        console.log(conditions);
        $.ajax({
            url:requestUrl,
            type: 'GET',
            traditional: true,
            data: {'condition':conditions,'pager':pager},
            dataType: 'JSON',
            success: function(response){
                $.Hide('#shade,#loading');
                if (response.status){
                    alert(1);
                    initGlobal(response.data.table_config);
                }
            }
        })
    }

     // 初始化全局变量
    function initGlobal(globalDict) {
        $.each(globalDict, function (k, v) {
            NB_GLOBAL_DICT[k] = v;
        })
    }

    nw.extend({
        // 添加选中,
        'initMenu':function(target){
          $(target).addClass('active').sibling.removeClass('active');
        },

        'AddSearchCondition':function(ths){
            var $duplicate = $(ths).parent().parent().clone(true);
            $duplicate.find('.fa-plus-square').addClass('fa-minus-square').removeClass('fa-plus-square');
            $duplicate.find('a[onclick="$.AddSearchCondition(this)"]').attr('onclick', "$.RemoveSearchCondition(this)");

            $duplicate.appendTo($(ths).parent().parent().parent());
        },

        'Hide': function (target) {
            $(target).addClass('hide');
        },

        'Show': function (target) {
            $(target).removeClass('hide');
        },


        'DataList': function(url){
            requestUrl = url;
            initialize(1);
            //bindMenuFunction();
            //bindMultiSelect();
            //bindSearchCondition();
        }

    });
})(jQuery);