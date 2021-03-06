<?php require_once "preamble.php"; ?><!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Theme Ontology util</title>
<?php include "header.php"; ?>

    <script>
        function updateButtonStatus()
        {
            var val = $('#fieldVerify').is(':checked');
            $('#commitbutton').attr("disabled", !val);
        }

    </script>

</head>

<body>
<?php include "navbar.php"; ?>

<div class="container">
<?php
    $submit = $_POST["submit"];
    $action = $_POST["action"];
    $response = "";
    $result = "";

    if($submit == "commit") {
        require_once("pythonlib.php");

        if ($action == "runtests")
        {
            $out = tstp_pyrun('webtask.test_formatting 2>&1');
            echo "<h1>webtask.test_formatting</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.test_integrity 2>&1');
            echo "<h1>webtask.test_integrity</h1><pre>" . htmlentities($out) . "</pre>\n";
        }
        elseif ($action == "importgit")
        {
            $out = tstp_pyrun('webtask.importgit 2>&1');
            echo "<h1>webtask.importgit</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.cache_queries 2>&1');
            echo "<h1>webtask.cache_queries</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.maintenance 2>&1');
            echo "<h1>webtask.maintenance</h1><pre>" . htmlentities($out) . "</pre>\n";
            $out = tstp_pyrun('webtask.test_integrity 2>&1');
            echo "<h1>webtask.test_integrity</h1><pre>" . htmlentities($out) . "</pre>\n";
        }
        echo "<p>Task " . $action . " completed.</p>";
    }
?>

    <div class="row">
        <div class="col-md-6">
            <div class="basebox">
                Admin utilities.
            </div>
        </div>
        <div class="col-md-6">
            <div class="alert alert-info">
                <form method="post" enctype="multipart/form-data">
                    <fieldset class="form-group">
                        <label for="action">What?</label>
                        <select id="action" name="action">
                            <option value="nothing">&lt;nothing selected&gt;</option>
                            <option value="importgit">Import data from GIT repository "theming/notes".</option>
                            <option value="runtests">Run tests on GIT repository "theming/notes".</option>
                        </select>
                    </fieldset>

                    <fieldset class="form-group">
                        <input id="fieldVerify" type="checkbox" OnChange="updateButtonStatus()">
                        <label for="fieldVerify">Are you sure you want to execute this function?</label>
                    </fieldset>

                    <button id="commitbutton" type="submit" name="submit" value="commit" class="btn btn-primary" disabled>Do It!</button>
                    <button type="submit" name="submit" value="cancel" class="btn btn-danger">Cancel</button>
                </form>
            </div>
        </div>
    </div>


</div>


<?php include "footer.php"; ?>

</body>
</html>
