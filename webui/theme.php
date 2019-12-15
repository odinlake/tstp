<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<?php
	$THEME = $_GET['name'];
    $THME_URL = urlencode($THEME);
?>
<head>
	<meta charset="UTF-8">
	<title>Theme Ontology theme: <?php echo $THEME; ?></title>

<?php include "header.php"; ?>

    <script>
        var g_objType = "theme";
        var g_objName = "<?php echo $THEME; ?>";
        var g_objFields = [ "name", "title", "description" ];
        var g_objInfoBoxes = [ "parents", "children" ];
    	var g_objData;
    </script>
    <script type="text/javascript" src="js/tstp_objinfo.js"></script>

    <script>
        $(document).ready(function () {
            loadTablesOnReady();
        });

        function makeThemeLink(data, color = null)
        {
            urldata = encodeURIComponent(data);
            iframe = ''; 
            if (color)
            {
                return '<A style="color:' + color + ';" href="theme.php?name=' + urldata + '">' 
                    + data + iframe + '</A>';
            }
            return "<A href=\"theme.php?name=" + urldata + "\">" + data + iframe + "</A>";
        }

        function makeStoryLink(data, color = null)
        {
            urldata = encodeURIComponent(data);
            pwid = "preview" + data.hashCode();
            href = " href=\"story.php?name=" + urldata + "\"";
            pwurl = "storystub.php?name=" + urldata;
            iframe = ' <iframe id="' + pwid + 
                    '" frameborder="0" scrolling="no" class="previewer" dsrc="' + pwurl + '"></iframe>';
            jstags = " onmouseover='showPreview(\"" + pwid + "\")'";
            jstags += " onmouseout='hidePreview(\"" + pwid + "\")'";
            return "<A " + jstags + href + ">" + data + iframe + "</A>";
        }

        function loadPreview(frame) {
            frame.attr("src", frame.attr("dsrc"));
            /* // doesn't work because iframe content is loaded async
            frame.load(resizeIframe);
            function resizeIframe() {
                var h = frame.contents().find("body").height();
                console.log(h);
                frame.height(h);
            }
            */
        }

        function showPreview(name) {
            var obj = $("#" + name);
            if (!obj.attr("src")) loadPreview(obj);
            obj.show();
        }

        function hidePreview(name) {
            $("#" + name).hide();
        }

        function loadTablesOnReady() {
            $(document).ready(function() {
                $('#stories_datatable').DataTable( {
                    "ajax": 'json.php?type=storytheme&fields=name1,weight,motivation&f2=' + encodeURIComponent(g_objName) + '&slimit=200&rlimit=10000',
                    "pageLength" : 50,
                    "paging" : false,
                    "searching": false,
                    "order": [
                        [ 1, "asc" ],
                        [ 0, "asc" ],
                    ],

                    "columnDefs" : [
                        {
                            "render": function ( data, type, row ) {
                                urldata = encodeURIComponent(data);
                                html = makeStoryLink(data);
                                return html;
                            },
                            "className": "theme-cell",
                            "targets": 0,
                        },
                        {
                            "targets": 1,
                        },
                        {
                            "width": "60%",
                            "className": "description-cell",
                            "targets": 2,
                        },
                    ],
                    "initComplete": function(settings, json) {
                        $('#loading_message').css('display','none');
                    }
                } );
            } );

            $(document).ready(function() {
                $('#children_datatable').DataTable( {
                    "pageLength" : 50,
                    "paging" : false,
                    "searching": false,
                    "order": [
                        [ 0, "asc" ],
                    ],

                    "columnDefs" : [
                        {
                            "render": function ( data, type, row ) {
                                return makeThemeLink(data);
                            },
                            "className": "tstp-theme-cell",
                            "targets": 0,
                            "width": "20%",
                        },
                        {
                            "className": "tstp-description-cell",
                            "targets": 1,
                        },
                    ]
                } );
            } );

        }
    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container main-body">

<?php // Basic information //?>
    <div class="row">
        <div id="div_maininfo" class="basebox">

            <div class="col-md-12">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <div style="float:right;"><H4><span class="label label-theme">theme</span></H4></div>
                        <H4><?php echo $THEME; ?></H4>
                    </div>
                    <div class="panel-body"><div id="div_description"></div></div>
                </div>
            </div>

            <div class="col-md-12">
                <H4>List of Parent Themes</H4>
                <div id="div_parents"></div>
            </div>
        </div>
    </div>

<?php // Children TABLE //?>
    <div class="row">
        <div id="div_datatable" class="col-md-12 hpad0">
            <div class="basebox">
                <H4>List of Child Themes</H4>
                <table id="children_datatable" class="display table table-striped" cellspacing="0" width="100%">
                    <thead>
                        <tr>
                            <th>Theme</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                </table>
            </div>
        </div>
    </div>

<?php // Stories TABLE //?>
    <div class="row">
        <div id="div_datatable" class="col-md-12 hpad0">
            <div class="basebox">
                <H4>List of Stories</H4>
                <table id="stories_datatable" class="display table table-striped" cellspacing="0" width="100%">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Weight</th>
                            <th>Motivation</th>
                        </tr>
                    </thead>
                </table>
            </div>
        </div>
    </div>

    <div id="loading_message" class="row">
        <div class="basebox">loading...</div>
    </div>

</div>

<?php include "footer.php"; ?>

</body>
</html>
