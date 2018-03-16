<?php
//https://scihub.copernicus.eu/dhus/odata/v1/Products?q=footprint:%22Intersects(POLYGON((19.83%2043.27,21.66%2043.29,21.64%2042.65,20.45%2042.67)))%22&$orderby=IngestionDate%20desc

function shortURL($longURL) {
    $data = array("longUrl" => "$longURL");
    $data_string = json_encode($data);
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyDS6tMQdPf4knUMU3QCwFEdxDMsXkLg8sc');
    curl_setopt ($ch, CURLOPT_HTTPHEADER, Array("Content-Type: application/json"));
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);
    curl_setopt($ch, CURLOPT_POST, TRUE);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
    $return = curl_exec($ch);
    curl_close($ch);
    return json_decode($return, true); 
}

function locationRequest() { 
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'https://exxo:exxopass123@scihub.copernicus.eu/dhus/search?q=(platformname:Sentinel-2)%20AND%20footprint:"Intersects(POLYGON((19.83%2043.27,21.66%2043.29,21.64%2042.65,20.45%2042.67,19.83%2043.27)))"&format=json');
    curl_setopt($ch, CURLOPT_GET, TRUE);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
    $return = curl_exec($ch);
    curl_close($ch);
    return $return;
}

function decideURLID($xmlResult) {
    foreach($xmlResult->entry as $ent) {
        if (substr($ent->title,0,2) == "S2") {
            echo $ent->{'title'}."\n";
            echo $ent->{'m:properties'}->{'d:ContentDate'}->{'d:Start'}."\n";
            return $ent;
        }
    }
    return false;
}

function get_string_between($string, $start, $end){
    $string = ' ' . $string;
    $ini = strpos($string, $start);
    if ($ini == 0) return '';
    $ini += strlen($start);
    $len = strpos($string, $end, $ini) - $ini;
    return substr($string, $ini, $len);
}

$globalCreationDate = "";

function parseResponseAsJSON($response) {
    $fullMail = "";
    
    $locationSummary = "";
    $baseDownloadURL = "";
    $basePreviewURL = "";
    $uuid = storedUUIDCheck();
    $tempUUID = "";
    $firstRun = true;

    $json_array = json_decode($response, true);
    
    foreach ($json_array as $k=>$v) {
        foreach($v as $rk=>$rv) {
            if($rk == "entry") {
                foreach($rv as $pk => $property) {
                    foreach($property as $ek=>$entry) {
                        if($ek == "summary") {
                            $locationSummary = $entry;
                            echo "Location summary: ".$locationSummary."\n";
                        }
                        else if($ek == "link") {
                            foreach($entry as $lk=>$link) {
                                if($link["rel"] == NULL) {
                                    $baseDownloadURL = $link["href"];
                                    echo "Base download: ".$baseDownloadURL."\n";
                                }
                                else if ($link["rel"] == "icon"){
                                    $basePreviewURL = $link["href"];
                                    echo "Base preview: ".$basePreviewURL."\n";
                                }
                            }
                            $part1Url = "https://";
                            $part2Url = "exxo:exxopass123@";
                            $part3Url = substr($baseDownloadURL, 8);
                            $downloadURL = $part1Url . $part2Url . $part3Url;
                            $part3Url = substr($basePreviewURL, 8);
                            $previewURL = $part1Url . $part2Url . $part3Url;
                        }
                        else if($ek == "id") {
                            if($firstRun == true) {
                                $firstRun = false;
                                if($uuid != false) {
                                    $tempUUID = $entry;
                                    if($uuid == $entry) {
                                        break 4;
                                    }
                                }
                                else if($uuid != $entry ) {
                                    $uuid = $entry;
                                }
                                else {
                                    break 4;
                                }
                            }
                            else {
                                if ($uuid == $entry) {
                                    break 4;
                                }
                            }
                        }
                        if($locationSummary != "" && $previewURL != "" && $downloadURL != "" ) {
                            $mailText = "Location summary: ".$locationSummary."\n"."Access location preview: ".shortURL($previewURL)["id"]."\n"."Download location: ".shortURL($downloadURL)["id"]."\n";
                            $headers = 'From: hello@thebranko.com';
                            $fullMail = $fullMail.$mailText."==================================\n";
                        }
                    }
                }
            }
        }
    }
    $file = "UUIDStore.txt";
    file_put_contents($file, $uuid);
    if ($fullMail != "") {
        $headers = 'From: hello@thebranko.com';
        $didSend = mail("lpopovic@aob.rs","New location update",$fullMail,$headers);
        mail("bne.rca@gmail.com","New location update",$fullMail,$headers);
        echo $fullMail;
    }
}

function storedUUIDCheck() {
    $file = "UUIDStore.txt";
    $storedUUID = file_get_contents($file);

    if($storedUUID) {
        return $storedUUID;
    }
    return false;
}

function sateliteTypeChecker($sateliteType) {
    return substr($sateliteType,0,2) == "S2";
}

function parseResponseAsXML($response) {
    // $xml= simplexml_load_string($response); 
   
    // $e =  decideURLID($xml);
    // if (!$e) {
    //     echo "will return";
    //     return;
    // }
    // $urlId = $e->{'id'};
    // //$xml->entry[0]->id;
    // $part1Url = "https://";
	// $part2Url = "exxo:exxopass123@";
	// $part3Url = substr($urlId, 8);
	// $logURL = $part1Url . $part2Url . $part3Url;
    // $downloadURL = $logURL.'/$value';
    // $previewURL = $logURL.'/Products'."('Quicklook')".'/$value';
    // $title = $e->title;
    // $ttt = $e->{"m:properties"}->{"d:ContentDate"}->{"d:Start"};

    // $file = "UUIDStore.txt";
    // $current = file_get_contents($file);
    
    // $mailText = "";
    // if($current == false || $current != $urlId) {
    //     file_put_contents($file, $urlId);
    //     $mailText = "New location update!\nLocation summary: ".$title."\n"."Access location preview: ".$previewURL."\n"."Download location: ".$downloadURL."\nTTT ".$e->{'m:properties'}->{'d:ContentDate'}->{'d:Start'}."\n";
    //     $headers = 'From: hello@thebranko.com';
    //     $didSend = mail("lpopovic@aob.rs","New location update",$mailText,$headers);
    //     mail("bne.rca@gmail.com","New location update",$mailText,$headers);
    //     echo "Did Send Email ".$didSend."\n";
    // }
    // else {
    //     $mailText = "No geolocation update";
    // }

    // echo $mailText;
}

$resp = locationRequest();
parseResponseAsJSON($resp);

?>