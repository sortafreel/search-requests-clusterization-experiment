import logging
from json import JSONDecodeError
from types import MappingProxyType
from typing import Any, Literal, Type

import httpx
from fastapi.encoders import jsonable_encoder
from httpx import ConnectError, ConnectTimeout, HTTPStatusError, ReadTimeout
from pydantic import ValidationError

from web_app.models.base import SafeModel
from web_app.tools import RetryableException

logger = logging.getLogger(__name__)


def _validate_request_input(
    method: Literal["POST", "PATCH", "PUT", "GET"] = "POST",
    data: dict[str, Any] | None = None,
    json_data: dict | list | None = None,
) -> None:
    if method not in ("POST", "PATCH", "PUT", "GET"):
        raise ValueError(f"Disallowed method for `request_api` function: {method}")
    if method in ("POST", "PATCH", "PUT"):
        if json_data and data:
            raise ValueError("Only one of `data` or `json_data` can be provided.")
    else:
        if json_data or data:
            raise ValueError(
                f"`data` or `json_data` aren't allowed for the provided method ({method})."
            )


def _validate_request_output(
    resp: httpx.Response,
    url: str,
    validator: Type[SafeModel] | None = None,
    validate_list: bool = False,
    label: str = "",
) -> dict | list[dict]:
    try:
        if validator:
            if validate_list:
                output = [jsonable_encoder(validator(**x)) for x in resp.json()]  # NOQA
            else:
                output = jsonable_encoder(validator(**resp.json()))  # NOQA
        else:
            output = resp.json()
    except (TypeError, ValidationError, JSONDecodeError) as er:
        logger.error(
            f"Can't validate resource ({url}) ({label} | validator: {validator} | "
            f"validate_list: {validate_list}) "
            f"output ({resp.text}): {er} ({type(er)})"
        )
        raise RetryableException(f"{er}\n{label}")
    except Exception as er:
        # TODO Same as above
        logger.error(
            f"Unexpected error when validating resource ({url}) "
            "({label}) service output ({resp.text}): {er} ({type(er)})"
        )
        raise RetryableException(f"{er}\n{label}")
    return output


async def _async_request(
    client: httpx.AsyncClient,
    url: str,
    label: str,
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
    json_data: dict | list | None = None,
    auth: tuple[str, str] | None = None,
    method: Literal["POST", "PATCH", "PUT", "GET"] = "POST",
) -> httpx.Response:
    try:
        if json_data:
            resp = await client.request(
                method=method,
                url=url,
                auth=auth,
                json=json_data,
                headers=MappingProxyType(headers) if headers else None,
                follow_redirects=True,
            )
        elif data:
            resp = await client.request(
                method=method,
                url=url,
                auth=auth,
                data=MappingProxyType(data),
                headers=MappingProxyType(headers) if headers else None,
                follow_redirects=True,
            )
        else:
            resp = await client.request(
                method=method,
                url=url,
                auth=auth,
                headers=MappingProxyType(headers) if headers else None,
                follow_redirects=True,
            )
        resp.raise_for_status()
        return resp
    # Not handling as a decorator as it seems to cause unexpected errors with asyncio
    except (ConnectError, ConnectTimeout, ReadTimeout) as er:
        logger.error(
            f"Can't connect to the resource ({url}) (async | {label}): {er} ({type(er)}). Retrying."
        )
        raise RetryableException(f"{er}\n{label}")
    except HTTPStatusError as er:
        logger.error(
            f"Response error from the resource ({url}) (async | {label}): {er} ({type(er)}). Retrying."
        )
        raise RetryableException(f"{er}\n{label}")
    except Exception as er:
        logger.error(
            f"Unexpected error when connecting to the resource ({url}) "
            f"(async | {label}): {er}. Retrying."
        )
        raise RetryableException(f"{er}\n{label}")


async def async_request_api(
    client: httpx.AsyncClient,
    url: str,
    label: str,
    headers: dict[str, str] | None = None,
    data: dict[str, Any] | None = None,
    json_data: dict | list | None = None,
    auth: tuple[str, str] | None = None,
    validator: Type[SafeModel] | None = None,
    validate_list: bool = False,
    method: Literal["POST", "PATCH", "PUT", "GET"] = "POST",
) -> dict | list[dict]:
    _validate_request_input(method=method, data=data, json_data=json_data)
    resp = await _async_request(
        client=client,
        url=url,
        headers=headers,
        data=data,
        json_data=json_data,
        auth=auth,
        method=method,
        label=label,
    )
    output = _validate_request_output(
        resp=resp,
        url=url,
        validator=validator,
        validate_list=validate_list,
        label=label,
    )
    return output
