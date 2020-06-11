from OpenSSL import crypto
import traceback

saml_certs = ['MIIEUjCCAzqgAwIBAgIJAN6uoFTKjqEZMA0GCSqGSIb3DQEBCwUAMIGVMQswCQYDVQQDDAJDQTEX\nMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTATBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMC\nVVMxEzARBgNVBAgMCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6Y2hvYXAwMjkyLnByZy1kYy5kaGwu\nY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMjAwNTE2MTkxMTQ4WhcNMjgwNzE3MTI0MDQwWjBfMQww\nCgYDVQQDDANTVFMxCzAJBgNVBAYTAkRTMQ8wDQYDVQQIDAZWTXdhcmUxDzANBgNVBAcMBlZNd2Fy\nZTEPMA0GA1UECgwGVk13YXJlMQ8wDQYDVQQLDAZWTXdhcmUwggEiMA0GCSqGSIb3DQEBAQUAA4IB\nDwAwggEKAoIBAQC1SOoP1Ed2GqhFcaIcWUlGwWGV1TrpAu+oVZKQhy96xZPoFK9LDef9qXna1oFE\ny/iSLBsmUOIlBvW4lH6hcQNqbu5hthb0tl1uR7tSvXkAbsEuJtoXUmbOo9l2RUoXYT0tBR3E2uIH\nnIrqaGEAfugsi4D3yCbQFe6Hqgz+L7SL10JfAsTRQF8No/0VI5S5ucZ3Aag9myUiHfYI2URJHF8R\nr15uoJnbM4p2hmPvdQnxQ9mjtscG7HiNdsW7gUl3VAO04YTdEdW5L3ckP8jARP/cCJ4QBqOb0LRv\n0oOiLjjbuSILezvCdQAJLWmt4DkOgweYNsAkz5kBo5f1FUjoRPntAgMBAAGjgdkwgdYwCwYDVR0P\nBAQDAgXgMDsGA1UdEQQ0MDKBDmVtYWlsQGFjbWUuY29thwSlSEuqghpjemNob2FwMDI5Mi5wcmct\nZGMuZGhsLmNvbTAdBgNVHQ4EFgQUvSNJwExJp9dtC/W2PAl7aFKH3howHwYDVR0jBBgwFoAUCj7x\nYqqTHjTTs0Isz1gbIThAG20wSgYIKwYBBQUHAQEEPjA8MDoGCCsGAQUFBzAChi5odHRwczovL2N6\nY2hvYXAwMjkyLnByZy1kYy5kaGwuY29tL2FmZC92ZWNzL2NhMA0GCSqGSIb3DQEBCwUAA4IBAQB8\nUh9Uu/SUM73Thz3Y+uK/Oh145k8pLURdJysOLuTxMl5SyVeH1cLR4+mH3Mys0H1ezvZ0/s6Hakzk\n0eIHN5Wvssj7O8iI1yFPnhUoU8pphUOIBwsqo2oVJtedrS9C3R5QKP2PENgymMbIskepuUjxh98M\nXjsgPTZCpru/S+Ogzb6dHe0ihEz4ITL4XdeHDh5CmnAykZnEOgDGOKgam2btmlO5sVWmEpN0Ts9X\nBVvwblYBlm+G+DRwTFU4bfBfpoqBSXLI3KMT5dBaD+GXm9VsQ+dPrf35fM6fNz7/KBPpMRBwN3Uq\n9/xJAcrpJk9ycfuZxNLmjf1OLIb0ArH29Nk8', 'MIIEFTCCAv2gAwIBAgIJANhTHJYjYaO8MA0GCSqGSIb3DQEBCwUAMIGVMQswCQYDVQQDDAJDQTEX\nMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTATBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMC\nVVMxEzARBgNVBAgMCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6Y2hvYXAwMjkyLnByZy1kYy5kaGwu\nY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMTgwNzIwMTI0MDQwWhcNMjgwNzE3MTI0MDQwWjCBlTEL\nMAkGA1UEAwwCQ0ExFzAVBgoJkiaJk/IsZAEZFgd2c3BoZXJlMRUwEwYKCZImiZPyLGQBGRYFbG9j\nYWwxCzAJBgNVBAYTAlVTMRMwEQYDVQQIDApDYWxpZm9ybmlhMSMwIQYDVQQKDBpjemNob2FwMDI5\nMi5wcmctZGMuZGhsLmNvbTEPMA0GA1UECwwGVk13YXJlMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A\nMIIBCgKCAQEAriLCKjB2A+5xmGOnpzGv/9j2sg7rx5HWL+sUimg/2RXoHP+Wc2P0ff+eLeUrQY5u\nHVLjVKruBrv1fg0hSPLJ5ErVHjAIMTdNnkLAB1r3u0iPzGtyXXgyS4ue58NQj/1OFjfCmhAD0fB1\nRG3cpUpsU2MMgG6NRmVkha2L3zn6y+xGVZL+PoOoHC6ZpxTJzgk0KPMnEA4g7Bp8Se09MFWXjmRG\nETTGXbXwkH7qmK8T4MiWhXdudv+gQsYp3XW5kbW+LEs2ZGteGC9XYZl7uSbZaBz+mcrWGoYF1mYB\nq/WM36Xdlla0OjehdqeRVrRvGYCai+tpj7B5HsVL2dLtMOIFqwIDAQABo2YwZDAdBgNVHQ4EFgQU\nCj7xYqqTHjTTs0Isz1gbIThAG20wHwYDVR0RBBgwFoEOZW1haWxAYWNtZS5jb22HBH8AAAEwDgYD\nVR0PAQH/BAQDAgEGMBIGA1UdEwEB/wQIMAYBAf8CAQAwDQYJKoZIhvcNAQELBQADggEBAJSfz+94\nQS+8dizCUpuus2KIwYuSXG7cW2tYNDCceP8I/MiFo1hAT72u+a//zUPO76algB0yaWrsr79J019t\n6jAdovS8rHeMTM2mWdEW7/1+Q/I8jw3E138cw8sxIKkQviLP7wiqQUJ3BFJxhcYzFgutrJwRjVS2\n5QF1V/L17Ja8n9JryCBTzNLF3qDwiVPRimL4guo4Uyzrep3MMusJGHPDkW95qshEHPr7fsuWFqtp\nAz0wRdv6re9J+4DXZgkgzdEe4kQyJHy9NPHEPPjosMJ13Jqm0Bw2Gf4tA2qc/ml/JCqDHwHsjwgp\n6bkrAbSU0vMFY7Uk7y+3+JzbhgF58XQ=']

trusted = ['-----BEGIN CERTIFICATE-----\nMIIDpzCCAo+gAwIBAgIJAMEdFu7VYhk/MA0GCSqGSIb3DQEBCwUAMIGV\nMQswCQYDVQQDDAJDQTEXMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTAT\nBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMCVVMxEzARBgNVBAgM\nCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6Y2hvYXAwMjkyLnByZy1kYy5k\naGwuY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMTgwNjI2MTE0ODA4WhcN\nMjgwNjIwMTE1NzU0WjAYMRYwFAYDVQQDDA1zc29zZXJ2ZXJTaWduMIIB\nIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyif52qQp2xjTJhiF\nV7WRUHTD1x8OKM7moevcya/eMk/MuSJUT/qgNvj/eo3e/MhxveHz5BpS\ngUx/FBivT2w0x2M8/nIoFNIXeJq5uSCqBoXXLEb9eSBjn4JkMRd5VNr9\nUA3lLaja2l6w6Zsg7mO2WTe0L4h8lF2ee7B9yFfKBQMU66exTo8GJMqt\n6Ojr7sJmaPwmLW8t2eIjawRDlSl5KM2VaC93BQ28QzyzZEdcb7582Hru\n1HUMeYMis+FbCkYFLyuwc4ObaP3iSOKHCjmkuy+8QK4NtkfLMbNrdUcz\nI9InYcxq04dI2QGNxExycF8WcvTjnmp+ygqdpcrcRRYMPwIDAQABo3Yw\ndDALBgNVHQ8EBAMCBeAwJQYDVR0RBB4wHIIaY3pjaG9hcDAyOTIucHJn\nLWRjLmRobC5jb20wHQYDVR0OBBYEFC6oXfDQSb0edQd780DWicTtnRnP\nMB8GA1UdIwQYMBaAFFf98Ks5vG1pWx5VsZzb23rzPBeFMA0GCSqGSIb3\nDQEBCwUAA4IBAQB+IGiZbQau/b4FM65yMd7VziEJRSRy0MkEaBtqUnLg\ngxUaInD7+luYPK52UK9D9GUlrfW4EROp5RgXcWsVRVVe7EtsP8z2x50G\nTap8n7W4w1a2KrOlJ4e1Ffmqy93j2WXwnkidx0JI5wAdugtZdn6u0FZr\nZl9N3RB97NIYFL+33967x7A37/PbbZJjZ/2BhTY62StigsZ0TaHhaOLt\nH3uMKSTei/6mYB54kLLHv3BNasRI0u3C3jpc8kS0bgvuYntuqPYBPdjO\nVTG3jEAikqA17P8hPX/dwsUYgZ/R/4c2o9JNpxFbSuS8phu7eB4Kt/k5\nknR+JwPQODgWnz5KgYub\n-----END CERTIFICATE-----', '-----BEGIN CERTIFICATE-----\nMIIEFTCCAv2gAwIBAgIJAMSR5oG0bjCWMA0GCSqGSIb3DQEBCwUAMIGV\nMQswCQYDVQQDDAJDQTEXMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTAT\nBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMCVVMxEzARBgNVBAgM\nCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6Y2hvYXAwMjkyLnByZy1kYy5k\naGwuY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMTgwNjIzMTE1NzU0WhcN\nMjgwNjIwMTE1NzU0WjCBlTELMAkGA1UEAwwCQ0ExFzAVBgoJkiaJk/Is\nZAEZFgd2c3BoZXJlMRUwEwYKCZImiZPyLGQBGRYFbG9jYWwxCzAJBgNV\nBAYTAlVTMRMwEQYDVQQIDApDYWxpZm9ybmlhMSMwIQYDVQQKDBpjemNo\nb2FwMDI5Mi5wcmctZGMuZGhsLmNvbTEPMA0GA1UECwwGVk13YXJlMIIB\nIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAm9LV1bDK4WGvbjrn\nKGLdMnafyNBgya/e4Gg7xgoZldsXJfwLEGqnVrSFLzrNceYhu0D5nFlj\nAaGe0Yfwwbe3PifpRazbpXHGG92b+tES0quPzQes8blCrUjSxI/RlFmU\nxrm/6ZijJin8uWp5ksV9ujMyKCdh/cTQlgyminQu2PD3HD0RwWi3uefC\nysqVediAQo7eAPqQXsCX0UaYvCtW/+cBKdYquub5tr7yg6f4lCxrxFH6\nm96gjUWfqDr9VucJL6LQmFoxYb3L7LVpt/DFbjYnZrtgJnzyeg8mpS2k\nj17oRAYKs2ykrmY5A6LWE9HPcsaniDgtUiVf45qAVeOJiQIDAQABo2Yw\nZDAdBgNVHQ4EFgQUV/3wqzm8bWlbHlWxnNvbevM8F4UwHwYDVR0RBBgw\nFoEOZW1haWxAYWNtZS5jb22HBH8AAAEwDgYDVR0PAQH/BAQDAgEGMBIG\nA1UdEwEB/wQIMAYBAf8CAQAwDQYJKoZIhvcNAQELBQADggEBABzh0uKY\nyjJ7xT2EF6P8+arupZQH0qZnHnKcIZCxfVzEo2CP277TBHVnbOXxHORy\n6PmUTiOTfjvfpsitYUdtT8Vg3Rel8XR5oPKwidwePUIoYs2Ukql4mZab\nk4U4bRCF3a6gkFaVDVkWHbfzZUq6x4ZDQ+P5k/0BgWZa3hC4jdO6mwrE\nw4cnUQajaVcvvuc35Mc/pojilwUw7Jqm72wwfiXZvPKQWYyf8rt/bOHS\nuOp+2AAXpQlMKH5Il8DTvlutvrZYk13JyV5TeDmBHk8qQLrQ74nfaxNe\nB6YzheFWthTbQIXESZE/Wp2ofrZ3KzHAnqL9Ubqwjw5CnO6Uplf8FXw=\n-----END CERTIFICATE-----', '-----BEGIN CERTIFICATE-----\nMIIDpzCCAo+gAwIBAgIJANpXlC4ruBgrMA0GCSqGSIb3DQEBCwUAMIGV\nMQswCQYDVQQDDAJDQTEXMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTAT\nBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMCVVMxEzARBgNVBAgM\nCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6Y2hvYXAwMjkyLnByZy1kYy5k\naGwuY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMTgwNzIzMTIzMDU0WhcN\nMjgwNzE3MTI0MDQwWjAYMRYwFAYDVQQDDA1zc29zZXJ2ZXJTaWduMIIB\nIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsJfmTQIQte/b4FU8\nCzvyDrjZIOs2JMIX6ME/nsgVNcgHLfUznYfNIUoPIVnpB5lZL3qKpCNe\ndE8M5v2KY4YKyE9eeajjtrbiGfXqlh15a698WVoSogM/oU5scsZpnk0/\nDcKnO2iQcSySl9jeJcRW2Zcl08SQl5Enth5HkuC1NgvlJub8IZjnSWvB\njxrj1Q9bQtGlyH4xJFuvy6ev2mXlSyMXm4xHLD10J1o+bnpRRxnMAT6x\nkcfSgAzDiCqnIHmKpM1zyjxaMaavw/0T8y7lxzTwI7f9lsPMrkJ3wlac\nMJKEy9TaOScesu8iE54p28vAU16qiouRdinQ5HHINMt/NwIDAQABo3Yw\ndDALBgNVHQ8EBAMCBeAwJQYDVR0RBB4wHIIaY3pjaG9hcDAyOTIucHJn\nLWRjLmRobC5jb20wHQYDVR0OBBYEFNJDpwmKFcxV5tZ+V5m/QeWfZv4D\nMB8GA1UdIwQYMBaAFAo+8WKqkx4007NCLM9YGyE4QBttMA0GCSqGSIb3\nDQEBCwUAA4IBAQAZjiTxc0XEhDEvQZkNjTRmG0X+4GPrXMJFoG/KMCkg\nyDoZpRnbnfWoeGDdS964v+NTYzcSWt7c1npg2r7NgaMAK9AmCm9H1/89\nZ94LgwTuqqwWYHjpJlhojsRl7ES4/h9WaS6xBbfT5yrD6HI2PZmEb7Pe\n8hbZS0OkeQQ/Ev5lgIK0VO6naAdqReXGyptsd3nzn8lrO7EMULj6Y4L0\nkE9OVB88ErCR4vf1UlRjKE/UmfaGACiMcxDiYHFJQCSi3VxSzO19sHbo\n9CA67bbyOy/WimYNFwproArS3jdEr6nLFCadRcJrVJE7dw0WnEfq4bA9\nkZWOLgGOJwliKzO45lKw\n-----END CERTIFICATE-----', '-----BEGIN CERTIFICATE-----\nMIIEFTCCAv2gAwIBAgIJANhTHJYjYaO8MA0GCSqGSIb3DQEBCwUAMIGV\nMQswCQYDVQQDDAJDQTEXMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTAT\nBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMCVVMxEzARBgNVBAgM\nCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6Y2hvYXAwMjkyLnByZy1kYy5k\naGwuY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMTgwNzIwMTI0MDQwWhcN\nMjgwNzE3MTI0MDQwWjCBlTELMAkGA1UEAwwCQ0ExFzAVBgoJkiaJk/Is\nZAEZFgd2c3BoZXJlMRUwEwYKCZImiZPyLGQBGRYFbG9jYWwxCzAJBgNV\nBAYTAlVTMRMwEQYDVQQIDApDYWxpZm9ybmlhMSMwIQYDVQQKDBpjemNo\nb2FwMDI5Mi5wcmctZGMuZGhsLmNvbTEPMA0GA1UECwwGVk13YXJlMIIB\nIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAriLCKjB2A+5xmGOn\npzGv/9j2sg7rx5HWL+sUimg/2RXoHP+Wc2P0ff+eLeUrQY5uHVLjVKru\nBrv1fg0hSPLJ5ErVHjAIMTdNnkLAB1r3u0iPzGtyXXgyS4ue58NQj/1O\nFjfCmhAD0fB1RG3cpUpsU2MMgG6NRmVkha2L3zn6y+xGVZL+PoOoHC6Z\npxTJzgk0KPMnEA4g7Bp8Se09MFWXjmRGETTGXbXwkH7qmK8T4MiWhXdu\ndv+gQsYp3XW5kbW+LEs2ZGteGC9XYZl7uSbZaBz+mcrWGoYF1mYBq/WM\n36Xdlla0OjehdqeRVrRvGYCai+tpj7B5HsVL2dLtMOIFqwIDAQABo2Yw\nZDAdBgNVHQ4EFgQUCj7xYqqTHjTTs0Isz1gbIThAG20wHwYDVR0RBBgw\nFoEOZW1haWxAYWNtZS5jb22HBH8AAAEwDgYDVR0PAQH/BAQDAgEGMBIG\nA1UdEwEB/wQIMAYBAf8CAQAwDQYJKoZIhvcNAQELBQADggEBAJSfz+94\nQS+8dizCUpuus2KIwYuSXG7cW2tYNDCceP8I/MiFo1hAT72u+a//zUPO\n76algB0yaWrsr79J019t6jAdovS8rHeMTM2mWdEW7/1+Q/I8jw3E138c\nw8sxIKkQviLP7wiqQUJ3BFJxhcYzFgutrJwRjVS25QF1V/L17Ja8n9Jr\nyCBTzNLF3qDwiVPRimL4guo4Uyzrep3MMusJGHPDkW95qshEHPr7fsuW\nFqtpAz0wRdv6re9J+4DXZgkgzdEe4kQyJHy9NPHEPPjosMJ13Jqm0Bw2\nGf4tA2qc/ml/JCqDHwHsjwgp6bkrAbSU0vMFY7Uk7y+3+JzbhgF58XQ=\n-----END CERTIFICATE-----', '-----BEGIN CERTIFICATE-----\nMIIDpzCCAo+gAwIBAgIJAPVdItTp11IwMA0GCSqGSIb3DQEBCwUAMIGV\nMQswCQYDVQQDDAJDQTEXMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTAT\nBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMCVVMxEzARBgNVBAgM\nCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6c3RsYXAwMDM3LnByZy1kYy5k\naGwuY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMTgwNzIzMTI1MTQ2WhcN\nMjgwNzE3MTMwMTMwWjAYMRYwFAYDVQQDDA1zc29zZXJ2ZXJTaWduMIIB\nIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsl9CCxMbR18wpk+7\nWrGamK4/PHg4IpP3urcSnfuvMyoplNIRCbfu9u+jSZyAaF3kEdBlRaGT\nj6h3m7d1rAEydJkJUzExP6ywaTOfkwXyHHIZsMVkkyv/KFzJ8wPNrnZs\nwXAj/+YKeTGpuUs8uE/66WAvGBPUoOlikERdtWtmyhrGUiglq7UnIlY7\npuFAW5xMvTUk7F5+v8+seW0yvzzcJKP4zsyx393VwEL8E5Xf87O2FMxL\nqFtgowvzivdq670kfTttAQMFMT/vhkSY7uD2XIxUtis0f58yp9xVtSFz\nXVcN4jJYFI8iFRo8FicCXvm8uiKa0CPoFo8IeVuIEqw+DwIDAQABo3Yw\ndDALBgNVHQ8EBAMCBeAwJQYDVR0RBB4wHIIaY3pzdGxhcDAwMzcucHJn\nLWRjLmRobC5jb20wHQYDVR0OBBYEFF9OnTdl7ohC/+9k1rbT6A1CFEV0\nMB8GA1UdIwQYMBaAFOkiPZl/5D/lskpzGEi7zGSQ8bSeMA0GCSqGSIb3\nDQEBCwUAA4IBAQArAmmTsPiG9yjv03qbKAmNgckDlR1fnFO1tno6lo98\nFdA5dGVNDg84TEq6Mu0iGSHyNFTko6gRlA6fNc0V9iYlxf5kPjWE6U9+\nFvAScDbqE0xlhcICbnIhaJsKbSJQtRJoMF3v88qBitFWm+bN1BHU/Ykz\nC/fa5JoJReagtcs8OToJ1CFjuH7ah8qNImeOSMUwPnKVsKUPQkeZ8jJ9\n7+uoHcs4ZRbIo65UgAGpTGCmFFk3biJn3LZArJ0U3HK3U+y/wbNbbaXf\nNOhh6cWkay1XpHUzzvV8xLYrLrJJ8gLfFAa9vShAcZMbwx2dGFcA1Ptn\nQjAIOD8lwGriTBLnbqPu\n-----END CERTIFICATE-----', '-----BEGIN CERTIFICATE-----\nMIIEFTCCAv2gAwIBAgIJAPnM5MdKAgtgMA0GCSqGSIb3DQEBCwUAMIGV\nMQswCQYDVQQDDAJDQTEXMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTAT\nBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMCVVMxEzARBgNVBAgM\nCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6c3RsYXAwMDM3LnByZy1kYy5k\naGwuY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMTgwNzIwMTMwMTMwWhcN\nMjgwNzE3MTMwMTMwWjCBlTELMAkGA1UEAwwCQ0ExFzAVBgoJkiaJk/Is\nZAEZFgd2c3BoZXJlMRUwEwYKCZImiZPyLGQBGRYFbG9jYWwxCzAJBgNV\nBAYTAlVTMRMwEQYDVQQIDApDYWxpZm9ybmlhMSMwIQYDVQQKDBpjenN0\nbGFwMDAzNy5wcmctZGMuZGhsLmNvbTEPMA0GA1UECwwGVk13YXJlMIIB\nIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA+j/hig6FcX9px6yG\nQT3m/UHqGZlonSsMSwt00xv8Sk4gSbEgejxU9muO/3HLdLkVRc5hKG7n\nrYzvokNovzT6eQN97X22pM5yWuzgNrDlXliiU+UWhe+IFunmw4lTksjd\nN8atM1OpERqcDEi4avmgfYzwcdBgX91xSzgRnfrzD4aXTzdvjaANkVjU\nxe3fat+784ryd09EcSgOibT6APTqFV6GHqUPXg+004/MBP6Zj+j+COtk\nFbIFNtPkn8jJAGhHuSqO23mS3Wf3iIOZ9Qfu8Ws/z27ThwdbZ500z2eG\nKTVbBTeGN0JNbXmfmLG3gYSsF5vMCLKhAcb7H6amerTOlwIDAQABo2Yw\nZDAdBgNVHQ4EFgQU6SI9mX/kP+WySnMYSLvMZJDxtJ4wHwYDVR0RBBgw\nFoEOZW1haWxAYWNtZS5jb22HBH8AAAEwDgYDVR0PAQH/BAQDAgEGMBIG\nA1UdEwEB/wQIMAYBAf8CAQAwDQYJKoZIhvcNAQELBQADggEBAItTLhOM\nvx6Vwj6Kl/MqDZQQJ5nEKZbqBHNUcv5ypWwYfZ7iNIEfQs/1Dq7/4moH\nn6kfz0aZefQSeoUqgN1Hpmgs837iGL1NI+w8J4DlRGc5uwC2U7OhfR8G\nL2Ge3y55sCikdR+eSwrNsWkAhVetUvY5DmvUKBcDRTjrYjDhEHvB5GVX\n2razLpIs8/Uh4H/3hhKB2TFtJCNAc7SQq3jvK0P5aYXtv2JMfp1mcrQ2\nmCOJ+w5e4v8Rp0+Oh0xBiSUt744KUaTbjVpn0R+XsaaEcFdR1aup5JfQ\nxp42h+H2B9TdizUxKlhyfTSIuoJRRiwEg3rBj8IEzOrsKmYHtrQsRO4=\n-----END CERTIFICATE-----', '-----BEGIN CERTIFICATE-----\nMIIEUjCCAzqgAwIBAgIJAN6uoFTKjqEZMA0GCSqGSIb3DQEBCwUAMIGV\nMQswCQYDVQQDDAJDQTEXMBUGCgmSJomT8ixkARkWB3ZzcGhlcmUxFTAT\nBgoJkiaJk/IsZAEZFgVsb2NhbDELMAkGA1UEBhMCVVMxEzARBgNVBAgM\nCkNhbGlmb3JuaWExIzAhBgNVBAoMGmN6Y2hvYXAwMjkyLnByZy1kYy5k\naGwuY29tMQ8wDQYDVQQLDAZWTXdhcmUwHhcNMjAwNTE2MTkxMTQ4WhcN\nMjgwNzE3MTI0MDQwWjBfMQwwCgYDVQQDDANTVFMxCzAJBgNVBAYTAkRT\nMQ8wDQYDVQQIDAZWTXdhcmUxDzANBgNVBAcMBlZNd2FyZTEPMA0GA1UE\nCgwGVk13YXJlMQ8wDQYDVQQLDAZWTXdhcmUwggEiMA0GCSqGSIb3DQEB\nAQUAA4IBDwAwggEKAoIBAQC1SOoP1Ed2GqhFcaIcWUlGwWGV1TrpAu+o\nVZKQhy96xZPoFK9LDef9qXna1oFEy/iSLBsmUOIlBvW4lH6hcQNqbu5h\nthb0tl1uR7tSvXkAbsEuJtoXUmbOo9l2RUoXYT0tBR3E2uIHnIrqaGEA\nfugsi4D3yCbQFe6Hqgz+L7SL10JfAsTRQF8No/0VI5S5ucZ3Aag9myUi\nHfYI2URJHF8Rr15uoJnbM4p2hmPvdQnxQ9mjtscG7HiNdsW7gUl3VAO0\n4YTdEdW5L3ckP8jARP/cCJ4QBqOb0LRv0oOiLjjbuSILezvCdQAJLWmt\n4DkOgweYNsAkz5kBo5f1FUjoRPntAgMBAAGjgdkwgdYwCwYDVR0PBAQD\nAgXgMDsGA1UdEQQ0MDKBDmVtYWlsQGFjbWUuY29thwSlSEuqghpjemNo\nb2FwMDI5Mi5wcmctZGMuZGhsLmNvbTAdBgNVHQ4EFgQUvSNJwExJp9dt\nC/W2PAl7aFKH3howHwYDVR0jBBgwFoAUCj7xYqqTHjTTs0Isz1gbIThA\nG20wSgYIKwYBBQUHAQEEPjA8MDoGCCsGAQUFBzAChi5odHRwczovL2N6\nY2hvYXAwMjkyLnByZy1kYy5kaGwuY29tL2FmZC92ZWNzL2NhMA0GCSqG\nSIb3DQEBCwUAA4IBAQB8Uh9Uu/SUM73Thz3Y+uK/Oh145k8pLURdJysO\nLuTxMl5SyVeH1cLR4+mH3Mys0H1ezvZ0/s6Hakzk0eIHN5Wvssj7O8iI\n1yFPnhUoU8pphUOIBwsqo2oVJtedrS9C3R5QKP2PENgymMbIskepuUjx\nh98MXjsgPTZCpru/S+Ogzb6dHe0ihEz4ITL4XdeHDh5CmnAykZnEOgDG\nOKgam2btmlO5sVWmEpN0Ts9XBVvwblYBlm+G+DRwTFU4bfBfpoqBSXLI\n3KMT5dBaD+GXm9VsQ+dPrf35fM6fNz7/KBPpMRBwN3Uq9/xJAcrpJk9y\ncfuZxNLmjf1OLIb0ArH29Nk8\n-----END CERTIFICATE-----']


def add_x509_pem_header(text):
    """ Append proper prefix and suffix text to a certificate.
    """
    prefix = '-----BEGIN CERTIFICATE-----'
    if text.startswith(prefix):
        return text
    ret_text = "\n".join((prefix, text, "-----END CERTIFICATE-----"))
    return ret_text


store = crypto.X509Store()

for i in range(len(trusted)):
    if i == 1:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, trusted[i])
        continue
    print(trusted[i])
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, trusted[i])
    store.add_cert(cert)

chain = [
    crypto.load_certificate(
        crypto.FILETYPE_PEM,
        add_x509_pem_header(c)) for c in saml_certs]

signing_chain = chain[:]

while True:
    for i in range(len(chain)):
        try:
            storeCtx = crypto.X509StoreContext(store, chain[i])
            try:
                store.add_cert(chain[i])
            except crypto.Error as e:
                pass  # Duplicate cert case
            del chain[i]
            break  # Break for loop, go back to top of while.
        except Exception as e:
            pass  # Verification failed, keep trying other certs.
    else:
        break  # For loop finished executing; break while loop.
if chain:
    # chain list should be empty if we've verified everything.
    raise Exception(
        'One or more certificates cannot be verified.')
