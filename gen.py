import ctypes
import os
import platform
import threading
import time
import uuid
from random import choice, randint
from typing import Optional

import httpx
from colorama import Fore, init

from staticstrings import StaticStrings

# init colorama
init(autoreset=True)

# load constants

strings = StaticStrings("constants.json")


class counter:
  count = 0


red, blue, green, yellow = [Fore.RED, Fore.BLUE, Fore.GREEN, Fore.YELLOW]


def get_timestamp():
  time_idk = time.strftime('%H:%M:%S')
  timestamp = f'[\x1b[90m{time_idk}\x1b[0m]'
  return timestamp


def initialize():
  if not os.path.isfile("proxies.txt"):
    with open("proxies.txt", "w") as f:
      f.write("")
  if platform.system() != "Windows":
    os.system('clear')
    return
  os.system('cls')


def update_console_title(title):
  if platform.system() == "Windows":
    ctypes.windll.kernel32.SetConsoleTitleW(title)  # type: ignore
  else:
    print(f"\33]0;{title}\a", end='', flush=True)


def generate_random_ip():
  return f"13.{randint(104, 107)}.{randint(0, 255)}.{randint(0, 255)}"


def gen(proxy):
  while True:
    url = strings.api_url
    headers = {
        "Content-Type": strings.content_type,
        "Sec-Ch-Ua":
        '"Opera GX";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
        "User-Agent": strings.user_agent,
        "X-Forwarded-For": generate_random_ip()
    }
    data = {"partnerUserId": str(uuid.uuid4())}

    try:
      if proxy:
        credentials, host = proxy.split('@')
        user, password = credentials.split(':')
        host, port = host.split(':')
        formatted_proxy = f"http://{user}:{password}@{host}:{port}"
        response = httpx.post(url,
                              json=data,
                              headers=headers,
                              proxies={
                                  'http': formatted_proxy,
                                  'https': formatted_proxy
                              },
                              timeout=5)
      else:
        response = httpx.post(url, json=data, headers=headers, timeout=5)

      if response.status_code == 200:
        token = response.json().get('token')
        if token:
          counter.count += 1
          update_console_title(
              f"Opera Gx Promo Generator | Tokens Generated: {counter.count}")
          link = f"https://discord.com/billing/partner-promotions/1180231712274387115/{token}"
          with open("promos.txt", "a") as f:
            f.write(f"{link}\n")
          print(f"{get_timestamp()} Generated Promo Link: {link}")
      elif response.status_code == 429:
        print(f"{get_timestamp()} {strings.rate_limited_message}")
      else:
        print(
            f"{get_timestamp()} {strings.request_failed_message}{response.status_code}"
        )
    except Exception as e:
      print(f"{get_timestamp()} Request Failed: {e}")


def main(num_threads: int = 1,
         interval_ms: int = 3000,
         limit: Optional[int] = 100):
  initialize()
  num_threads = num_threads if num_threads > 0 else int(
      input(f"{get_timestamp()} {blue} Enter Number Of Threads : "))
  with open("proxies.txt") as f:
    proxies = f.read().splitlines()

  current_count = 0
  if not os.path.isfile("promos.txt"):
    with open("promos.txt", "w") as f:
      f.write("")
  else:
    with open("promos.txt") as f:
      current_count = len(f.readlines())
  threads = []
  if limit and current_count > limit:
    print(f"{get_timestamp()} {red} Too many promos generated! ({limit})",
          "Exiting...",
          sep="\n")
    return
  for _ in range(num_threads):
    proxy = choice(proxies) if proxies else None
    thread = threading.Thread(target=gen, args=(proxy, ))
    threads.append(thread)

  for thread in threads:
    thread.start()

  try:
    while True:
      time.sleep(int(interval_ms / 1000))
  except KeyboardInterrupt:
    for thread in threads:
      thread.join()


if __name__ == "__main__":
  main()
