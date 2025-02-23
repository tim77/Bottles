# details.py
#
# Copyright 2020 brombinmirko <send@mirko.pm>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk

import webbrowser, re

from .dialog import BottlesDialog
from bottles.empty import BottlesEmpty

@Gtk.Template(resource_path='/com/usebottles/bottles/installer-entry.ui')
class BottlesInstallerEntry(Gtk.Box):
    __gtype_name__ = 'BottlesInstallerEntry'

    '''Get widgets from template'''
    label_name = Gtk.Template.Child()
    label_description = Gtk.Template.Child()
    btn_install = Gtk.Template.Child()
    btn_manifest = Gtk.Template.Child()

    def __init__(self, window, configuration, installer, plain=False, **kwargs):
        super().__init__(**kwargs)

        '''Init template'''
        self.init_template()

        '''Common variables'''
        self.window = window
        self.runner = window.runner
        self.configuration = configuration
        self.installer = installer

        '''Populate widgets'''
        self.label_name.set_text(installer[0])
        self.label_description.set_text(installer[1].get("Description"))

        '''Signal connections'''
        self.btn_install.connect('pressed', self.execute_installer)
        self.btn_manifest.connect('pressed', self.open_manifest)

    '''Open installer manifest'''
    def open_manifest(self, widget):
        dialog_upgrade = BottlesDialog(
            parent=self.window,
            title=_("Manifest for {0}").format(self.installer[0]),
            message=_("This is the manifest for {0}.").format(self.installer[0]),
            log=self.runner.fetch_installer_manifest(self.installer[0],
                                                     self.installer[1]["Category"],
                                                      plain=True))
        dialog_upgrade.run()
        dialog_upgrade.destroy()

    '''Execute installer'''
    def execute_installer(self, widget):
        widget.set_sensitive(False)
        self.runner.run_installer(self.configuration,
                                  self.installer,
                                  self)

@Gtk.Template(resource_path='/com/usebottles/bottles/state-entry.ui')
class BottlesStateEntry(Gtk.Box):
    __gtype_name__ = 'BottlesStateEntry'

    '''Get widgets from template'''
    label_id = Gtk.Template.Child()
    label_comment = Gtk.Template.Child()
    label_creation_date = Gtk.Template.Child()
    btn_restore = Gtk.Template.Child()
    btn_remove = Gtk.Template.Child()
    btn_manifest = Gtk.Template.Child()

    def __init__(self, window, configuration, state, **kwargs):
        super().__init__(**kwargs)

        '''Init template'''
        self.init_template()

        '''Common variables'''
        self.window = window
        self.runner = window.runner
        self.state = state
        self.state_name = "State: {0}".format(state[0])
        self.configuration = configuration

        '''Populate widgets'''
        self.label_id.set_text(self.state_name)
        self.label_comment.set_text(self.state[1].get("Comment"))
        self.label_creation_date.set_text(self.state[1].get("Creation_Date"))
        if state[0] == configuration.get("State"):
            self.get_style_context().add_class("current-state")

        '''Signal connections'''
        self.btn_restore.connect('pressed', self.set_state)
        self.btn_manifest.connect('pressed', self.open_index)

    '''Set bottle state'''
    def set_state(self, widget):
        self.runner.set_bottle_state(self.configuration, self.state[0])

    '''Open state index'''
    def open_index(self, widget):
        dialog_upgrade = BottlesDialog(
            parent=self.window,
            title=_("Index for state {0}").format(self.state[0]),
            message=_("This is the index for {0}.").format(self.state[0]),
            log=self.runner.get_bottle_state_edits(self.configuration,
                                                   self.state[0],
                                                   True))
        dialog_upgrade.run()
        dialog_upgrade.destroy()

@Gtk.Template(resource_path='/com/usebottles/bottles/program-entry.ui')
class BottlesProgramEntry(Gtk.Box):
    __gtype_name__ = 'BottlesProgramEntry'

    '''Get widgets from template'''
    label_name = Gtk.Template.Child()
    btn_run = Gtk.Template.Child()
    btn_arguments = Gtk.Template.Child()
    btn_save_arguments = Gtk.Template.Child()
    btn_winehq = Gtk.Template.Child()
    btn_protondb = Gtk.Template.Child()
    btn_issues = Gtk.Template.Child()
    grid_arguments = Gtk.Template.Child()
    entry_arguments = Gtk.Template.Child()
    spinner_running = Gtk.Template.Child()

    def __init__(self, window, configuration, program, **kwargs):
        super().__init__(**kwargs)

        '''Init template'''
        self.init_template()

        '''Common variables'''
        self.window = window
        self.runner = window.runner
        self.configuration = configuration
        self.program_name = program[0]
        self.program_executable = program[1].split("\\")[-1]
        self.program_executable_path = program[1]

        '''Populate widgets'''
        self.label_name.set_text(self.program_name)

        '''Signal conenctions'''
        self.btn_run.connect('pressed', self.run_executable)
        self.btn_save_arguments.connect('pressed', self.save_arguments)
        self.btn_winehq.connect('pressed', self.open_winehq)
        self.btn_protondb.connect('pressed', self.open_protondb)
        self.btn_issues.connect('pressed', self.open_issues)
        self.btn_arguments.connect('toggled', self.toggle_arguments)

        '''Populate entry_arguments by configuration'''
        if self.program_executable in self.configuration["Programs"]:
            arguments = self.configuration["Programs"][self.program_executable]
            self.entry_arguments.set_text(arguments)

    '''Run executable'''
    def run_executable(self, widget):
        if self.program_executable in self.configuration["Programs"]:
            arguments = self.configuration["Programs"][self.program_executable]
        else:
            arguments = False
        self.runner.run_executable(self.configuration,
                                   self.program_executable_path,
                                   arguments)

    '''Save arguments'''
    def save_arguments(self, widget):
        arguments = self.entry_arguments.get_text()
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             self.program_executable,
                                                             arguments,
                                                             scope="Programs")
        self.configuration = new_configuration

    '''Toggle arguments grid'''
    def toggle_arguments(self, widget):
        status = widget.get_active()
        self.grid_arguments.set_visible(status)

    '''Open URLs'''
    def open_winehq(self, widget):
        query = self.program_name.replace(" ", "+")
        webbrowser.open_new_tab("https://www.winehq.org/search?q=%s" % query)

    def open_protondb(self, widget):
        query = self.program_name
        webbrowser.open_new_tab("https://www.protondb.com/search?q=%s" % query)

    def open_issues(self, widget):
        query = self.program_name.replace(" ", "+")
        webbrowser.open_new_tab("https://github.com/bottlesdevs/Bottles/issues?q=is:issue%s" % query)

@Gtk.Template(resource_path='/com/usebottles/bottles/dependency-entry.ui')
class BottlesDependencyEntry(Gtk.Box):
    __gtype_name__ = 'BottlesDependencyEntry'

    '''Get widgets from template'''
    label_name = Gtk.Template.Child()
    label_description = Gtk.Template.Child()
    label_category = Gtk.Template.Child()
    btn_install = Gtk.Template.Child()
    btn_remove = Gtk.Template.Child()
    btn_manifest = Gtk.Template.Child()

    def __init__(self, window, configuration, dependency, plain=False, **kwargs):
        super().__init__(**kwargs)

        '''Init template'''
        self.init_template()

        '''Common variables'''
        self.window = window
        self.runner = window.runner
        self.configuration = configuration
        self.dependency = dependency

        '''If dependency is plain text (placeholder)'''
        if plain:
            self.label_name.set_text(dependency)
            self.label_description.destroy()
            self.btn_install.set_visible(False)
            self.btn_remove.set_visible(False)
            return None

        '''Populate widgets'''
        self.label_name.set_text(dependency[0])
        self.label_description.set_text(dependency[1].get("Description"))
        self.label_category.set_text(dependency[1].get("Category"))

        '''Signal connections'''
        self.btn_install.connect('pressed', self.install_dependency)
        self.btn_remove.connect('pressed', self.remove_dependency)
        self.btn_manifest.connect('pressed', self.open_manifest)

        '''
        Set widgets status from configuration
        '''
        if dependency[0] in self.configuration.get("Installed_Dependencies"):
            self.btn_install.set_visible(False)
            self.btn_remove.set_visible(True)

    '''Open dependency manifest'''
    def open_manifest(self, widget):
        dialog_upgrade = BottlesDialog(
            parent=self.window,
            title=_("Manifest for {0}").format(self.dependency[0]),
            message=_("This is the manifest for {0}.").format(self.dependency[0]),
            log=self.runner.fetch_dependency_manifest(self.dependency[0],
                                                      self.dependency[1]["Category"],
                                                      plain=True))
        dialog_upgrade.run()
        dialog_upgrade.destroy()

    '''Install dependency'''
    def install_dependency(self, widget):
        widget.set_sensitive(False)
        self.runner.install_dependency(self.configuration,
                                       self.dependency,
                                       self)

    '''Remove dependency'''
    def remove_dependency(self, widget):
        widget.set_sensitive(False)
        self.runner.remove_dependency(self.configuration,
                                      self.dependency,
                                      self)


@Gtk.Template(resource_path='/com/usebottles/bottles/details.ui')
class BottlesDetails(Gtk.Box):
    __gtype_name__ = 'BottlesDetails'

    '''Get widgets from template'''
    label_name = Gtk.Template.Child()
    label_runner = Gtk.Template.Child()
    label_state = Gtk.Template.Child()
    label_update_date = Gtk.Template.Child()
    label_size = Gtk.Template.Child()
    label_disk = Gtk.Template.Child()
    notebook_details = Gtk.Template.Child()
    btn_winecfg = Gtk.Template.Child()
    btn_dependencies = Gtk.Template.Child()
    btn_debug = Gtk.Template.Child()
    btn_execute = Gtk.Template.Child()
    btn_browse = Gtk.Template.Child()
    btn_cmd = Gtk.Template.Child()
    btn_taskmanager = Gtk.Template.Child()
    btn_controlpanel = Gtk.Template.Child()
    btn_uninstaller = Gtk.Template.Child()
    btn_regedit = Gtk.Template.Child()
    btn_shutdown = Gtk.Template.Child()
    btn_reboot = Gtk.Template.Child()
    btn_killall = Gtk.Template.Child()
    btn_report_dependency = Gtk.Template.Child()
    btn_programs_updates = Gtk.Template.Child()
    btn_environment_variables = Gtk.Template.Child()
    btn_overrides = Gtk.Template.Child()
    btn_manage_runners = Gtk.Template.Child()
    btn_backup_config = Gtk.Template.Child()
    btn_backup_full = Gtk.Template.Child()
    btn_add_state = Gtk.Template.Child()
    switch_dxvk = Gtk.Template.Child()
    switch_dxvk_hud = Gtk.Template.Child()
    switch_esync = Gtk.Template.Child()
    switch_fsync = Gtk.Template.Child()
    switch_aco = Gtk.Template.Child()
    switch_discrete = Gtk.Template.Child()
    switch_virtual_desktop = Gtk.Template.Child()
    combo_virtual_resolutions = Gtk.Template.Child()
    combo_runner = Gtk.Template.Child()
    switch_pulseaudio_latency = Gtk.Template.Child()
    list_dependencies = Gtk.Template.Child()
    list_programs = Gtk.Template.Child()
    list_installers = Gtk.Template.Child()
    list_states = Gtk.Template.Child()
    progress_disk = Gtk.Template.Child()
    entry_environment_variables = Gtk.Template.Child()
    entry_overrides = Gtk.Template.Child()
    entry_state_comment = Gtk.Template.Child()
    pop_state = Gtk.Template.Child()
    grid_versioning = Gtk.Template.Child()

    def __init__(self, window, configuration=dict, **kwargs):
        super().__init__(**kwargs)

        '''Init template'''
        self.init_template()

        '''Common variables'''
        self.window = window
        self.runner = window.runner
        self.configuration = configuration

        '''Populate combo_runner'''
        for runner in self.runner.runners_available:
            self.combo_runner.append(runner, runner)

        '''Signal connections'''
        self.btn_winecfg.connect('pressed', self.run_winecfg)
        self.btn_dependencies.connect('pressed', self.show_dependencies)
        self.btn_debug.connect('pressed', self.run_debug)
        self.btn_execute.connect('pressed', self.run_executable)
        self.btn_browse.connect('pressed', self.run_browse)
        self.btn_cmd.connect('pressed', self.run_cmd)
        self.btn_taskmanager.connect('pressed', self.run_taskmanager)
        self.btn_controlpanel.connect('pressed', self.run_controlpanel)
        self.btn_uninstaller.connect('pressed', self.run_uninstaller)
        self.btn_regedit.connect('pressed', self.run_regedit)
        self.btn_shutdown.connect('pressed', self.run_shutdown)
        self.btn_reboot.connect('pressed', self.run_reboot)
        self.btn_killall.connect('pressed', self.run_killall)
        self.btn_report_dependency.connect('pressed', self.open_report_url)
        self.btn_programs_updates.connect('pressed', self.update_programs)
        self.btn_environment_variables.connect('pressed', self.save_environment_variables)
        self.btn_overrides.connect('pressed', self.save_overrides)
        self.btn_manage_runners.connect('pressed', self.window.show_runners_preferences_view)
        self.btn_backup_config.connect('pressed', self.backup_config)
        self.btn_backup_full.connect('pressed', self.backup_full)
        self.btn_add_state.connect('pressed', self.add_state)
        self.switch_dxvk.connect('state-set', self.toggle_dxvk)
        self.switch_dxvk_hud.connect('state-set', self.toggle_dxvk_hud)
        self.switch_esync.connect('state-set', self.toggle_esync)
        self.switch_fsync.connect('state-set', self.toggle_fsync)
        self.switch_aco.connect('state-set', self.toggle_aco)
        self.switch_discrete.connect('state-set', self.toggle_discrete_graphics)
        self.switch_virtual_desktop.connect('state-set', self.toggle_virtual_desktop)
        self.combo_virtual_resolutions.connect('changed', self.set_virtual_desktop_resolution)
        self.combo_runner.connect('changed', self.set_runner)
        self.switch_pulseaudio_latency.connect('state-set', self.toggle_pulseaudio_latency)
        self.entry_state_comment.connect('key-release-event', self.check_entry_state_comment)

    '''Set bottle configuration'''
    def set_configuration(self, configuration):
        self.configuration = configuration

        '''Lock signals preventing triggering'''
        self.switch_dxvk.handler_block_by_func(self.toggle_dxvk)
        self.switch_virtual_desktop.handler_block_by_func(self.toggle_virtual_desktop)
        self.combo_virtual_resolutions.handler_block_by_func(self.set_virtual_desktop_resolution)
        self.combo_runner.handler_block_by_func(self.set_runner)

        '''Get bottle/disk usage and set disk_fraction'''
        bottle_size = self.runner.get_bottle_size(configuration)
        disk_free = self.runner.get_disk_size()["free"]
        disk_fraction = (
            self.runner.get_disk_size(False)["used"] /
            self.runner.get_disk_size(False)["total"])

        '''Populate widgets from configuration'''
        parameters = self.configuration.get("Parameters")
        versioning = self.configuration.get("Versioning")
        self.notebook_details.get_nth_page(5).set_visible(versioning)
        self.label_name.set_text(self.configuration.get("Name"))
        self.label_runner.set_text(self.configuration.get("Runner"))
        self.label_state.set_text(str(self.configuration.get("State")))
        self.label_update_date.set_text(self.configuration.get("Update_Date"))
        self.label_size.set_text(bottle_size)
        self.label_disk.set_text(disk_free)
        self.progress_disk.set_fraction(disk_fraction)
        self.switch_dxvk.set_active(parameters["dxvk"])
        self.switch_dxvk_hud.set_active(parameters["dxvk_hud"])
        self.switch_esync.set_active(parameters["esync"])
        self.switch_fsync.set_active(parameters["fsync"])
        self.switch_discrete.set_active(parameters["discrete_gpu"])
        self.switch_virtual_desktop.set_active(parameters["virtual_desktop"])
        self.combo_virtual_resolutions.set_active_id(parameters["virtual_desktop_res"])
        self.combo_runner.set_active_id(self.configuration.get("Runner"))
        self.switch_pulseaudio_latency.set_active(parameters["pulseaudio_latency"])
        self.entry_environment_variables.set_text(parameters["environment_variables"])
        self.entry_overrides.set_text(parameters["dll_overrides"])
        self.grid_versioning.set_visible(self.configuration.get("Versioning"))

        '''Unlock signals'''
        self.switch_dxvk.handler_unblock_by_func(self.toggle_dxvk)
        self.switch_virtual_desktop.handler_unblock_by_func(self.toggle_virtual_desktop)
        self.combo_virtual_resolutions.handler_unblock_by_func(self.set_virtual_desktop_resolution)
        self.combo_runner.handler_unblock_by_func(self.set_runner)

        self.update_programs()
        self.update_dependencies()
        self.update_installers()
        self.update_states()

    '''Set active page'''
    def set_page(self, page):
        self.notebook_details.set_current_page(page)

    '''Show dependencies tab'''
    def show_dependencies(self, widget):
        self.set_page(2)

    '''Save DLL overrides'''
    def save_overrides(self, widget):
        overrides = self.entry_overrides.get_text()
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "dll_overrides",
                                                             overrides,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Save environment variables'''
    def save_environment_variables(self, widget):
        environment_variables = self.entry_environment_variables.get_text()
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "environment_variables",
                                                             environment_variables,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Populate list_programs'''
    def update_programs(self, widget=False):
        for w in self.list_programs: w.destroy()

        programs = self.runner.get_programs(self.configuration)

        if len(programs) == 0:
            return self.list_programs.add(BottlesEmpty(
                text=_("No programs found!"),
                icon="view-grid-symbolic",
                tip=_("The programs installed in the bottle will be listed here.")))

        for program in programs:
            self.list_programs.add(
                BottlesProgramEntry(self.window, self.configuration, program))

    '''Populate list_dependencies'''
    def update_dependencies(self, widget=False):
        for w in self.list_dependencies: w.destroy()

        supported_dependencies = self.runner.supported_dependencies.items()
        if len(supported_dependencies) > 0:
            for dependency in supported_dependencies:
                self.list_dependencies.add(
                    BottlesDependencyEntry(self.window,
                                           self.configuration,
                                           dependency))
            return

        if len(self.configuration.get("Installed_Dependencies")) > 0:
            for dependency in self.configuration.get("Installed_Dependencies"):
                self.list_dependencies.add(
                    BottlesDependencyEntry(self.window,
                                           self.configuration,
                                           dependency,
                                           plain=True))
            return

        return self.list_dependencies.add(BottlesEmpty(
            text=_("No dependencies found!"),
            icon="dialog-warning-symbolic",
            tip=_("There are no dependencies installed and we can't fetch from repository.")))

    '''Populate list_installers'''
    def update_installers(self, widget=False):
        for w in self.list_installers: w.destroy()

        supported_installers = self.runner.supported_installers.items()

        if len(supported_installers) > 0:
            for installer in supported_installers:
                self.list_installers.add(
                    BottlesInstallerEntry(self.window,
                                          self.configuration,
                                          installer))
            return

        return self.list_installers.add(BottlesEmpty(
            text=_("No installers found!"),
            icon="dialog-warning-symbolic",
            tip=_("We can't fetch the installers from the repository right now.")))

        for installer in supported_installers:
            self.list_installers.add(
                BottlesInstallerEntry(self.window,
                                      self.configuration,
                                      installer))

    '''Populate list_states'''
    def update_states(self, widget=False):
        if self.configuration.get("Versioning"):
            for w in self.list_states: w.destroy()

            states = self.runner.list_bottle_states(self.configuration).items()
            if len(states) > 0:
                for state in states:
                    self.list_states.add(
                        BottlesStateEntry(self.window,
                                          self.configuration,
                                          state))

    '''Toggle DXVK'''
    def toggle_dxvk(self, widget, state):
        if state:
            self.runner.install_dxvk(self.configuration)
        else:
            self.runner.remove_dxvk(self.configuration)

        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "dxvk",
                                                             state,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Toggle DXVK HUD'''
    def toggle_dxvk_hud(self, widget, state):
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "dxvk_hud",
                                                             state,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Toggle Esync'''
    def toggle_esync(self, widget, state):
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "esync",
                                                             state,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Toggle Fsync'''
    def toggle_fsync(self, widget, state):
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "fsync",
                                                             state,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Toggle ACO compiler'''
    def toggle_aco(self, widget, state):
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "aco_compiler",
                                                             state,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Toggle discrete graphics usage'''
    def toggle_discrete_graphics(self, widget, state):
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "discrete_gpu",
                                                             state,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Toggle virtual desktop'''
    def toggle_virtual_desktop(self, widget, state):
        resolution = self.combo_virtual_resolutions.get_active_id()
        self.runner.toggle_virtual_desktop(self.configuration,
                                           state,
                                           resolution)
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "virtual_desktop",
                                                             state,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Set virtual desktop resolution'''
    def set_virtual_desktop_resolution(self, widget):
        resolution = widget.get_active_id()
        if self.switch_virtual_desktop.get_active():
            self.runner.toggle_virtual_desktop(self.configuration,
                                               True,
                                               resolution)
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "virtual_desktop_res",
                                                             resolution,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Set (change) runner'''
    def set_runner(self, widget):
        runner = widget.get_active_id()
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "Runner",
                                                             runner)
        self.configuration = new_configuration

    '''Toggle pulseaudio latency'''
    def toggle_pulseaudio_latency(self, widget, state):
        new_configuration = self.runner.update_configuration(self.configuration,
                                                             "pulseaudio_latency",
                                                             state,
                                                             scope="Parameters")
        self.configuration = new_configuration

    '''Display file dialog for executable selection'''
    def run_executable(self, widget):
        file_dialog = Gtk.FileChooserDialog(_("Choose a Windows executable file"),
                                            self.window,
                                            Gtk.FileChooserAction.OPEN,
                                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        '''Create filters for allowed extensions'''
        filter_exe = Gtk.FileFilter()
        filter_exe.set_name(".exe")
        filter_exe.add_pattern("*.exe")

        filter_msi = Gtk.FileFilter()
        filter_msi.set_name(".msi")
        filter_msi.add_pattern("*.msi")

        file_dialog.add_filter(filter_exe)
        file_dialog.add_filter(filter_msi)

        response = file_dialog.run()

        if response == Gtk.ResponseType.OK:
            self.runner.run_executable(self.configuration,
                                       file_dialog.get_filename())

        file_dialog.destroy()

    '''Run wine executables and utilities'''
    def run_winecfg(self, widget):
        self.runner.run_winecfg(self.configuration)

    def run_winetricks(self, widget):
        self.runner.run_winetricks(self.configuration)

    def run_debug(self, widget):
        self.runner.run_debug(self.configuration)

    def run_browse(self, widget):
        self.runner.open_filemanager(self.configuration)

    def run_cmd(self, widget):
        self.runner.run_cmd(self.configuration)

    def run_taskmanager(self, widget):
        self.runner.run_taskmanager(self.configuration)

    def run_controlpanel(self, widget):
        self.runner.run_controlpanel(self.configuration)

    def run_uninstaller(self, widget):
        self.runner.run_uninstaller(self.configuration)

    def run_regedit(self, widget):
        self.runner.run_regedit(self.configuration)

    def run_shutdown(self, widget):
        self.runner.send_status(self.configuration, "shutdown")

    def run_reboot(self, widget):
        self.runner.send_status(self.configuration, "reboot")

    def run_killall(self, widget):
        self.runner.send_status(self.configuration, "kill")

    '''Validate entry_state input'''
    def check_entry_state_comment(self, widget, event_key):
        regex = re.compile('[@!#$%^&*()<>?/\|}{~:.;,"]')
        comment = widget.get_text()

        if(regex.search(comment) == None):
            self.btn_add_state.set_sensitive(True)
            widget.set_icon_from_icon_name(1, "")
        else:
            self.btn_add_state.set_sensitive(False)
            widget.set_icon_from_icon_name(1, "dialog-warning-symbolic")

    '''Add new state'''
    def add_state(self, widget):
        comment = self.entry_state_comment.get_text()
        if comment != "":
            self.runner.create_bottle_state(self.configuration, comment)
            self.entry_state_comment.set_text("")
            self.pop_state.popdown()

    '''Display file dialog for backup configuration'''
    def backup_config(self, widget):
        file_dialog = Gtk.FileChooserDialog(
            _("Select the location where to save the backup configuration"),
            self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        file_dialog.set_current_name("backup_%s.json" % self.configuration.get("Path"))

        response = file_dialog.run()

        if response == Gtk.ResponseType.OK:
            self.runner.backup_bottle(self.configuration,
                                      "configuration",
                                      file_dialog.get_filename())

        file_dialog.destroy()

    '''Display file dialog for backup archive'''
    def backup_full(self, widget):
        file_dialog = Gtk.FileChooserDialog(
            _("Select the location where to save the backup archive"),
            self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        file_dialog.set_current_name(
            "backup_%s.tar.gz" % self.configuration.get("Path"))

        response = file_dialog.run()

        if response == Gtk.ResponseType.OK:
            self.runner.backup_bottle(self.configuration,
                                      "full",
                                      file_dialog.get_filename())

        file_dialog.destroy()

    '''Open URLs'''
    @staticmethod
    def open_report_url(widget):
        webbrowser.open_new_tab("https://github.com/bottlesdevs/dependencies/issues/new/choose")
