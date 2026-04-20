import 'package:flutter/material.dart';

import 'app_controller.dart';
import 'formatters.dart';
import 'models.dart';

class GuardHomePage extends StatelessWidget {
  const GuardHomePage({
    required this.controller,
    super.key,
  });

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    final selectedSchedule = controller.selectedSchedule;
    final selectedRecord = controller.selectedAttendanceRecord;

    return Scaffold(
      appBar: AppBar(
        title: const Text('HRIS BPE Guard'),
        actions: [
          IconButton(
            onPressed: controller.isRefreshing
                ? null
                : () => controller.refreshData(),
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            onPressed: () => controller.logout(),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => controller.refreshData(),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _SummaryCard(controller: controller),
            if (controller.errorMessage != null) ...[
              const SizedBox(height: 12),
              _MessageBanner(
                tone: Colors.red.shade700,
                background: Colors.red.shade50,
                message: controller.errorMessage!,
              ),
            ],
            if (controller.infoMessage != null) ...[
              const SizedBox(height: 12),
              _MessageBanner(
                tone: Colors.green.shade700,
                background: Colors.green.shade50,
                message: controller.infoMessage!,
              ),
            ],
            const SizedBox(height: 16),
            _SectionTitle(
              title: 'Attendance Hari Ini',
              subtitle: 'Pilih schedule lalu lanjut check-in atau check-out.',
            ),
            const SizedBox(height: 12),
            _AttendanceActionCard(
              controller: controller,
              selectedSchedule: selectedSchedule,
              selectedRecord: selectedRecord,
            ),
            const SizedBox(height: 16),
            _SectionTitle(
              title: 'My Schedules',
              subtitle: 'Schedule yang sudah dipublish atau diapprove.',
            ),
            const SizedBox(height: 12),
            if (controller.schedules.isEmpty)
              const _EmptyCard(
                message: 'Belum ada schedule yang tersedia untuk user ini.',
              )
            else
              ...controller.schedules.map(
                (schedule) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: _ScheduleTile(
                    schedule: schedule,
                    isSelected: schedule.id == controller.selectedSchedule?.id,
                    onTap: () => controller.selectSchedule(schedule.id),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    final selected = controller.selectedSchedule;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFD6DCD4)),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            controller.session?.user.email ?? '-',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 8),
          Text('Status hari ini: ${controller.todayAttendanceStatus}'),
          const SizedBox(height: 4),
          Text('Schedule hari ini: ${controller.todaySchedules.length}'),
          if (selected != null) ...[
            const SizedBox(height: 4),
            Text(
              'Terpilih: ${selected.clientSiteName ?? 'Site #${selected.clientSiteId}'}'
              '${selected.sitePostName != null ? ' / ${selected.sitePostName}' : ''}',
            ),
          ],
        ],
      ),
    );
  }
}

class _AttendanceActionCard extends StatelessWidget {
  const _AttendanceActionCard({
    required this.controller,
    required this.selectedSchedule,
    required this.selectedRecord,
  });

  final AppController controller;
  final MyWorkSchedule? selectedSchedule;
  final AttendanceRecord? selectedRecord;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFD6DCD4)),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (selectedSchedule != null) ...[
            Text(
              selectedSchedule!.clientSiteName ?? 'Site #${selectedSchedule!.clientSiteId}',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              selectedSchedule!.sitePostName != null
                  ? selectedSchedule!.sitePostName!
                  : 'Tanpa post',
            ),
            const SizedBox(height: 4),
            Text(
              '${formatDate(selectedSchedule!.scheduledDate)} | '
              '${formatDateTime(selectedSchedule!.scheduledStartDateTime)} - '
              '${formatDateTime(selectedSchedule!.scheduledEndDateTime)}',
            ),
          ] else ...[
            const Text('Pilih schedule untuk lanjut presensi.'),
          ],
          const SizedBox(height: 16),
          Text('Check-in: ${formatDateTime(selectedRecord?.checkInDateTime)}'),
          const SizedBox(height: 4),
          Text('Check-out: ${formatDateTime(selectedRecord?.checkOutDateTime)}'),
          const SizedBox(height: 4),
          Text('Status record: ${selectedRecord?.attendanceStatus ?? '-'}'),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: FilledButton(
                  onPressed: controller.isSubmittingAttendance || !controller.canCheckIn
                      ? null
                      : controller.checkIn,
                  child: Text(
                    controller.isSubmittingAttendance ? 'Memproses...' : 'Check-in',
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton(
                  onPressed: controller.isSubmittingAttendance || !controller.canCheckOut
                      ? null
                      : controller.checkOut,
                  child: Text(
                    controller.isSubmittingAttendance ? 'Memproses...' : 'Check-out',
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ScheduleTile extends StatelessWidget {
  const _ScheduleTile({
    required this.schedule,
    required this.isSelected,
    required this.onTap,
  });

  final MyWorkSchedule schedule;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final borderColor = isSelected ? const Color(0xFF2F6F43) : const Color(0xFFD6DCD4);
    final backgroundColor = isSelected ? const Color(0xFFE9F3EC) : Colors.white;

    return InkWell(
      borderRadius: BorderRadius.circular(8),
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: borderColor),
        ),
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              schedule.clientSiteName ?? 'Site #${schedule.clientSiteId}',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              schedule.sitePostName ?? 'Post #${schedule.sitePostId ?? '-'}',
            ),
            const SizedBox(height: 4),
            Text(
              schedule.shiftTypeName ?? 'Shift #${schedule.shiftTypeId}',
            ),
            const SizedBox(height: 8),
            Text(formatDate(schedule.scheduledDate)),
            const SizedBox(height: 4),
            Text(
              '${formatDateTime(schedule.scheduledStartDateTime)} - '
              '${formatDateTime(schedule.scheduledEndDateTime)}',
            ),
            const SizedBox(height: 8),
            Text('Status schedule: ${schedule.scheduleStatus}'),
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({
    required this.title,
    required this.subtitle,
  });

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: 4),
        Text(subtitle),
      ],
    );
  }
}

class _EmptyCard extends StatelessWidget {
  const _EmptyCard({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFD6DCD4)),
      ),
      padding: const EdgeInsets.all(16),
      child: Text(message),
    );
  }
}

class _MessageBanner extends StatelessWidget {
  const _MessageBanner({
    required this.tone,
    required this.background,
    required this.message,
  });

  final Color tone;
  final Color background;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(8),
      ),
      padding: const EdgeInsets.all(12),
      child: Text(
        message,
        style: TextStyle(color: tone, fontWeight: FontWeight.w600),
      ),
    );
  }
}
