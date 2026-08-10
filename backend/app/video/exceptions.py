class VideoSourceError(RuntimeError):
    pass


class UnsupportedSourceTypeError(VideoSourceError):
    pass


class SourceAlreadyStartedError(VideoSourceError):
    pass


class SourceNotRunningError(VideoSourceError):
    pass


class SourceFrameUnavailableError(VideoSourceError):
    pass