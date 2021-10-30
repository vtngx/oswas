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

class InputTypes:
  CHECKBOX = "checkbox"
  COLOR = "color"
  DATE = "date"
  DATETIME_LOCAL = "datetime-local"
  EMAIL = "email"
  FILE = "file"
  IMAGE = "image"
  MONTH = "month"
  NUMBER = "number"
  PASSWORD = "password"
  RADIO = "radio"
  RANGE = "range"
  SEARCH = "search"#
  TEL = "tel"
  TEXT = "text"
  TIME = "time"
  URL = "url"
  WEEK = "week"

AuthKeywords = [
  'login', 'loginform', 'log in', 'signin', 'sign in', 'dang-nhap', 'Sign in'
]

BLACKLIST = [
  'logout', 'Logout', 'log out', 'Log out', 'thoat', 'Thoat', 'dangxuat', 'Dangxuat', 'dang xuat',
  'Dang xuat', 'logOut', 'LogOut', 'log Out', 'Log Out', 'dangXuat', 'DangXuat', 'dang Xuat', 'Dang Xuat'
]