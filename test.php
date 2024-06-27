<?php 

echo "Spouštím test.py";
$command = escapeshellcmd('/scripts/test.py');
$output = shell_exec($command);
echo $output;

?>