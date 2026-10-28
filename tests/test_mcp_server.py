"""企业大数据 MCP 服务合同测试。"""

import asyncio
import importlib.util
import unittest
from pathlib import Path
from unittest import TestCase
from unittest.mock import call, patch


SERVER_PATH = Path(__file__).parents[1] / "server" / "mcp_server.py"
SPEC = importlib.util.spec_from_file_location("enterprise_mcp_server", SERVER_PATH)
assert SPEC and SPEC.loader
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


class ContractTests(TestCase):
    def test_registered_tools_are_unchanged(self) -> None:
        tools = asyncio.run(server.mcp.list_tools())
        self.assertEqual(
            {tool.name for tool in tools},
            {
                "enterprise_get_keyword_search",
                "enterprise_get_enterprise_base_info",
                "enterprise_get_enterprise_holder_info",
                "enterprise_get_enterprise_invest_info",
                "enterprise_get_enterprise_branch_info",
                "enterprise_get_enterprise_main_person_info",
            },
        )

    def test_base_info_only_calls_remaining_three_products(self) -> None:
        with patch.object(
            server,
            "call_api",
            side_effect=[{"base": 1}, {"description": 1}, {"tags": 1}],
        ) as api:
            result = server.enterprise_get_enterprise_base_info("企业A全称")

        self.assertEqual(
            result,
            {
                "base_info": {"base": 1},
                "desc": {"description": 1},
                "tag": {"tags": 1},
            },
        )
        self.assertEqual(
            api.call_args_list,
            [
                call("66dbccbec7a7e3460f5e613f", {"matchKeyword": "企业A全称"}),
                call("6682b0b370f56cb7d77701e0", {"matchKeyword": "企业A全称"}),
                call("669e531ce1fd7bff82321d8d", {"matchKeyword": "企业A全称"}),
            ],
        )

    def test_removed_product_is_absent_from_runtime_and_readme(self) -> None:
        target = "66e55613ae988a28" + "c6db9259"
        removed_field = "business" + "_info"
        source = SERVER_PATH.read_text(encoding="utf-8")
        readme = (SERVER_PATH.parents[1] / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(target, source)
        self.assertNotIn(target, readme)
        self.assertNotIn(removed_field, source)
        self.assertNotIn(removed_field, readme)
        self.assertIn("主营方向", source)
        self.assertIn("主营方向", readme)


if __name__ == "__main__":
    unittest.main()
