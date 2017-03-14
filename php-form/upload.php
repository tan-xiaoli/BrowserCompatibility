<?php

// 允许上传的图片后缀
$allowedExts = array("png");

// 获取文件后缀
$temp=explode(".", $_FILES["file"]["name"]);
$extension = end($temp);

if($_FILES["file"]["type"]=="image/png" && in_array($extension, $allowedExts)) {
    if($_FILES["file"]["error"] > 0)     {
        echo "错误: ".$_FILES["file"]["error"]."<br>";
    } else {
        $upload_path = $_POST["path"];
        
        // 上传路径判断
        if(! file_exists($upload_path) || ! is_dir($upload_path)) {
            mkdir($upload_path, 0777, true);
        } else {
            echo "上传路径[.$upload_path]已存在!";
        }
        
        // 判断上传路径是否以/结尾
        if (substr($upload_path, -1) != "/") {
            $upload_path.= "/";
        }
        $upload_full_path = $upload_path.$_FILES["file"]["name"];

        // 如果文件已存在，删除
        if( file_exists($upload_full_path) && is_file($upload_full_path) ) {
            unlink($upload_full_path);
        }
        
        move_uploaded_file( $_FILES["file"]["tmp_name"], $upload_full_path );
        @header("HTTP/1.1 200 OK");
    }
}
else {
    echo "非法的文件格式.";
    @header("HTTP/1.1 400 BAS Request");
}
?>
