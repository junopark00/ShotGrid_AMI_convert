# :coding: utf-8

# convert_model.py

import urllib

import shotgun_api3


class ShotgunAction:
    def __init__(self, url) -> None:
        self._url = url
        self._sg = self.__connect_to_shotgrid()

    def __connect_to_shotgrid(self) -> shotgun_api3.Shotgun:
        """
        shotgrid api를 서버와 연결

        Returns:
            shotgun_api3.Shotgun: shotgrid 객체 생체
        """
        SERVER_PATH = "Your Shotgrid Server Path"
        SCRIPT_NAME = "Your Script"
        SCRIPT_KEY = "Your Script Key"
        return shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

    def get_entity_info(self, entity_type: str, id: str, fields: list) -> dict:
        """
        지정한 entity_type과 id을 기반으로 해당 레코드의 field값을 return

        Args:
            entity_type (str): 레코드를 검색하고자 하는 entity
            selected_id (str): 정보를 가져오고자 하는 레코드의 id
            fields (list): 가져오려는 필드값 리스트

        Returns:
            dict: _description_
        """
        return self._sg.find_one(entity_type, [['id', 'is', int(id)]], fields)
    
    def parse_url(self, logger) -> any:
        """
        Shotgrid로부터 받은 url의 정보를 파싱하여 return

        Returns:
            any: protocol(str), action(str), params(dict)
        """
        logger.info("Parsing full url received: %s" % self._url)

        # get the protocol used
        protocol, path = self._url.split(":", 1)
        logger.info("protocol: %s" % protocol)

        # extract the action
        action, params = path.split("?", 1)
        action = action.strip("/")
        logger.info("action: %s" % action)

        # extract the parameters
        params = params.split("&")
        p = {"column_display_names": [], "cols": []}
        for arg in params:
            key, value = map(urllib.parse.unquote, arg.split("=", 1))
            if key == "column_display_names" or key == "cols":
                p[key].append(value)
            else:
                p[key] = value
        params = p
        logger.info("params: %s" % params)
        return protocol, action, params
    
    
if __name__ == "__main__":
    sa = ShotgunAction()
    print(sa.get_entity_info("PublishedFile", 8, ["code"]))
