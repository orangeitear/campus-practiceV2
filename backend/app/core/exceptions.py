class BizException(Exception):
    """自定义业务异常类"""
    
    def __init__(self, code: int = 400, message: str = "业务异常"):
        self.code = code
        self.message = message
        super().__init__(self.message)


class NotFoundException(BizException):
    """资源不存在异常 (404)"""
    
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=404, message=message)


class UnauthorizedException(BizException):
    """未授权异常 (401)"""
    
    def __init__(self, message: str = "未授权，请先登录"):
        super().__init__(code=401, message=message)


class ForbiddenException(BizException):
    """无权限异常 (403)"""
    
    def __init__(self, message: str = "无权限访问"):
        super().__init__(code=403, message=message)


class ValidationException(BizException):
    """参数校验异常 (400)"""
    
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(code=400, message=message)