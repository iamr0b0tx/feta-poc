def validate_host(host):
    # todo: check if is valid ipv4/v6 or domain
    # if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host):
    #     raise HTTPException(status_code=400, detail="Invalid Host: Host must be IPv4 address")
    return host
