#!/usr/bin/python3 -u

import os
import io
import http.server
import PIL
import libcamera # sudo apt install python3-libcamera
import picamera2 # sudo apt install python3-picamera2

#https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf

port = 8000

class Server(http.server.ThreadingHTTPServer):

    def __init__(self):

        # set up http listern
        super().__init__(('', port), Handler)

        # suppress logging
        os.environ["LIBCAMERA_LOG_LEVELS"] = "3"

        # create camera object
        self.camera = picamera2.Picamera2()

        # find uncropped sizes
        sizes = []
        for sm in self.camera.sensor_modes:
            if sm["crop_limits"][0:2] == (0, 0):
                sizes.append(sm["size"])
        print(sizes)

        # configure
        print("available controls:", self.camera.camera_controls)
        size = min(sizes) # smallest uncropped native sensor mode
        config = self.camera.create_video_configuration({'format': 'BGR888', 'size': size})
        print("generated config:", config)
        config["controls"] = {
            "AfMode": libcamera.controls.AfModeEnum.Continuous,
            "AeMeteringMode": libcamera.controls.AeMeteringModeEnum.Matrix,
            "ExposureValue": -1
        }
        self.camera.configure(config)
        print("got config", self.camera.camera_configuration())

        # now ready to start
        self.camera.start()

class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        print(f"do_GET {self.path}")

        if self.path == "/":

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body style='background: black;'><img width='100%' src='/stream'/></body></html>")

        elif self.path == "/stream":

            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()

            while True:
                array = server.camera.capture_array("main")
                img = PIL.Image.fromarray(array)
                buf = io.BytesIO()
                img.save(buf, format="jpeg")
                data = bytes(buf.getbuffer())
                try:
                    self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + data + b"\r\n")
                    self.wfile.flush()
                except (ConnectionResetError, BrokenPipeError):
                    print("client went away")
                    break

        else:
                
            self.send_response(404)
            self.end_headers()


server = Server()
server.serve_forever()
