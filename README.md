# Jetson TX1 demo
## DEBUGGING
### How to start simple Flask web server for debugging
At the very beginning, make sure Flask has been installed in your setup.
If not, run 'pip install flask' to get it ready.
1. run below command in your setup
```shell
cd test
python cloud.py
```
2. open http://<board_ip_address>:5000 in your favorite web browser
3. done

### How to start the software on board
```shell
sudo python jetson.py
```

### How to send command to board
![open door](github.com/jia345/jetson/edit/master/doc/opendoor.png)
