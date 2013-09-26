from scrapy.exceptions import DropItem

class ItemSwitch(object):
    """Redirect Items to Appropriate Pipeline Handler"""

    def __init__(self):
        pass

    def process_item(self, item, spider):
        """Consumes item from spider and passes to correct handler asynchronously"""

        # extract the class of the item
        item_class = item.__class__.__name__

        # switch to handle item based on class type
        if item_class == "ScrapedUrl":
            pass #do something
        else:
            raise DropItem("No behavior defined for item of type %s" % item_class)
        
        # return item to next piece of pipeline
        return item

