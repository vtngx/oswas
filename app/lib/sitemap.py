import datetime

class Sitemap():

    def __init__(self, starting_url, links):
      self.starting_url = starting_url
      self.url_list = set(list(link["url"] for link in links))
      self.parent_urls = []
      self.url_tree = {}
      self.js_string = ""

    def build_xml(self):
        with open(f"sitemap.xml", "w") as f:
            f.writelines("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd\">\n")
            for url in self.url_list:
                clean_url = url.replace(self.starting_url, "/")

                if clean_url[-1:] != "/":
                    clean_url += "/"

                self.crawl_depth = clean_url.count("/") - 1

                if clean_url != "/":
                    self.parent = self.get_parent(clean_url)
                else:
                    self.parent = "/"

                if self.parent not in self.parent_urls and self.parent != "/":
                    self.parent_urls.append(self.parent)

                self.add_to_tree(clean_url)

                f.writelines("  <url>\n")
                f.writelines("    <loc>" + url + "</loc>\n")
                f.writelines(
                    "    <lastmod>" + datetime.datetime.now().strftime("%Y-%m-%d") + "</lastmod>\n")
                f.writelines("    <changefreq>daily</changefreq>\n")
                f.writelines("    <priority>1.0</priority>\n")
                f.writelines("  </url>\n")
            f.writelines("</urlset>")

    def get_parent(self, url):
      if url.count("/") == 2:
        return url
      elif url.count("/") > 2:
        temp = url.split("/")[1:-2]
        temp = "/" + "/".join(temp) + "/"
        return temp
      else:
        temp = url.split("/")[1:-2]
        temp = "/" + "/".join(temp) + "/"
        return temp

    def add_to_tree(self, url):
      if self.parent not in self.url_tree.keys():
        self.url_tree[self.parent] = []
      else:
        self.url_tree[self.parent].append(
          url.replace(self.parent, "/")
        )

    def build_visual(self):
      js_prefix = "    var chart_config = {\n" \
        "        chart: {\n" \
        "            container: \"#sitemap\",\n" \
        "            levelSeparation: 25,\n" \
        "            connectors: {" \
        "                type: \"step\",\n" \
        "                style: {" \
        "                    \"stroke-width\": 1\n" \
        "                }\n" \
        "            },\n" \
        "            node: {\n" \
        "                HTMLclass: \"treemap\"" \
        "            }\n" \
        "       },\n" \
        "       nodeStructure: {" \
        "           text: { name: \"" + self.starting_url + "\" },\n" \
        "           connectors: {" \
        "               style: {\n" \
        "                   'stroke': '#bbb',\n" \
        "                   'arrow-end': 'block-wide-long'\n" \
        "               }\n" \
        "           },\n" \
        "       children: [\n"
      js_nodes = ""
      parent_url_count = 1
      parent_url_length = len(self.url_tree)

      for parent_url in sorted(self.url_tree):
        if parent_url == "/":
          continue
        if parent_url_count == parent_url_length:
          js_nodes += "       {\n" \
            "           text: { name: \"" + parent_url + "\" },\n" \
            "           stackChildren: true,\n" \
            "           connectors: {\n" \
            "               style: {\n" \
            "                   'arrow-end': 'block-wide-long'\n" \
            "               }\n" \
            "           }"

          if len(self.url_tree[parent_url]) > 0:
            child_url_length = len(self.url_tree[parent_url])
            if child_url_length > 5:
              child_url_length = 5
            child_url_count = 1
            js_nodes += ",\n           children: [\n"
            for child_url in self.url_tree[parent_url]:
              if child_url_count == child_url_length:
                if child_url_length < 5:
                  js_nodes += "           { \n" \
                    "text: { name: \"" + child_url + "\" } }"
                else:
                  js_nodes += "           { \n" \
                    "text: { name: \"" + child_url + "\" } },"
                break
              else:
                js_nodes += "{ " \
                  "text: { name: \"" + child_url + "\" } },"
                child_url_count += 1

            js_nodes += "]\n"
          js_nodes += "}\n"
        else:
          js_nodes += "       {\n" \
            "           text: { name: \"" + parent_url + "\" },\n" \
            "           stackChildren: true,\n" \
            "           connectors: {\n" \
            "               style: {\n" \
            "                   'arrow-end': 'block-wide-long'\n" \
            "               }\n" \
            "           }"

          # need to plan children
          if len(self.url_tree[parent_url]) > 0:
            child_url_length = len(self.url_tree[parent_url])
            if child_url_length > 5:
              child_url_length = 5
            child_url_count = 1
            js_nodes += ",\n           children: [ \n"
            for child_url in sorted(self.url_tree[parent_url]):
              if child_url == "/": continue
              if child_url_count == child_url_length:
                if child_url_length < 5:
                  js_nodes += "           { \n" \
                    "text: { name: \"" + child_url + "\" } }"
                else:
                  js_nodes += "           { \n" \
                    "text: { name: \"" + child_url + "\" } },"
                break
              else:
                js_nodes += "{ " \
                  "text: { name: \"" + child_url + "\" } },"
                child_url_count += 1

            js_nodes += "]\n"

          js_nodes += "},\n"

          parent_url_count += 1

      js_suffix = "] }\n};\nnew Treant( chart_config );\n"
      self.js_string = (js_prefix + js_nodes + js_suffix)

      self.save()

    def save(self):
      with open(f"init_sitemap", "w") as f:
        f.writelines(self.js_string)