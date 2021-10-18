from os import stat


class TargetStatus:
  DOING   = "DOING"   # mới khởi tạo Target
  DONE    = "DONE"    # đã crawl xong
  CANCEL  = "CANCEL"  # user hủy giữa chừng

class LinkStatus:
  TODO  = "TODO"    # link chưa crawl
  DOING = "DOING"   # link đang crawl
  DONE  = "DONE"    # link đã crawl xong

class UserCrawlType:
  USER1   = "USER1"   # crawl as normal user 1
  USER2   = "USER2"   # crawl as normal user 2
  ADMIN   = "ADMIN"   # crawl as admin user
  NO_AUTH = None      # crawl without authen

AuthKeywords = [
  'login', 'loginform', 'log in', 'signin', 'sign in', 'dang-nhap', 'Sign in'
]