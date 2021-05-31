from sardana.macroserver.macro import imacro, Type, Optional


@imacro([['directory', Type.String, Optional, 'RemoteScanDir']])
def change_remote_dir(self, directory):
    self.setEnv('RemoteScanDir', '/media/nas/data/imaging/202002')
    self.output(self.getEnv('RemoteScanDir'))
