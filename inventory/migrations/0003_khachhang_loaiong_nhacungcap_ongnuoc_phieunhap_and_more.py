# Generated by Django 4.2.7 on 2025-04-30 09:40

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_waterpipecounthistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='KhachHang',
            fields=[
                ('ma_kh', models.AutoField(primary_key=True, serialize=False)),
                ('ten_kh', models.CharField(max_length=200)),
                ('sdt', models.CharField(max_length=15)),
                ('dia_chi', models.TextField()),
                ('ma_so_thue', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'verbose_name': 'Khách Hàng',
                'verbose_name_plural': 'Khách Hàng',
            },
        ),
        migrations.CreateModel(
            name='LoaiOng',
            fields=[
                ('ma_loai', models.AutoField(primary_key=True, serialize=False)),
                ('ten_loai', models.CharField(max_length=100)),
                ('mo_ta', models.TextField(blank=True, null=True)),
                ('don_vi_tinh', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Loại Ống',
                'verbose_name_plural': 'Loại Ống',
            },
        ),
        migrations.CreateModel(
            name='NhaCungCap',
            fields=[
                ('ma_ncc', models.AutoField(primary_key=True, serialize=False)),
                ('ten_ncc', models.CharField(max_length=200)),
                ('sdt', models.CharField(max_length=15)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('dia_chi', models.TextField()),
            ],
            options={
                'verbose_name': 'Nhà Cung Cấp',
                'verbose_name_plural': 'Nhà Cung Cấp',
            },
        ),
        migrations.CreateModel(
            name='OngNuoc',
            fields=[
                ('ma_ong', models.AutoField(primary_key=True, serialize=False)),
                ('ten_ong', models.CharField(max_length=100)),
                ('kich_thuoc', models.CharField(max_length=50)),
                ('chat_lieu', models.CharField(max_length=100)),
                ('ap_luc_toi_da', models.DecimalField(decimal_places=2, help_text='Đơn vị: bar', max_digits=10)),
                ('so_met_ton', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('anh_minh_hoa', models.ImageField(blank=True, null=True, upload_to='warehouse_images/')),
                ('ma_loai', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ong_nuoc', to='inventory.loaiong')),
            ],
            options={
                'verbose_name': 'Ống Nước',
                'verbose_name_plural': 'Ống Nước',
            },
        ),
        migrations.CreateModel(
            name='PhieuNhap',
            fields=[
                ('ma_phieu_nhap', models.AutoField(primary_key=True, serialize=False)),
                ('ngay_nhap', models.DateField(default=django.utils.timezone.now)),
                ('tong_tien', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('nguoi_tao', models.CharField(max_length=100)),
                ('ghi_chu', models.TextField(blank=True, null=True)),
                ('ma_ncc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phieu_nhap', to='inventory.nhacungcap')),
            ],
            options={
                'verbose_name': 'Phiếu Nhập',
                'verbose_name_plural': 'Phiếu Nhập',
            },
        ),
        migrations.CreateModel(
            name='PhieuXuat',
            fields=[
                ('ma_phieu_xuat', models.AutoField(primary_key=True, serialize=False)),
                ('ngay_xuat', models.DateField(default=django.utils.timezone.now)),
                ('tong_tien', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('nguoi_tao', models.CharField(max_length=100)),
                ('ghi_chu', models.TextField(blank=True, null=True)),
                ('ma_kh', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phieu_xuat', to='inventory.khachhang')),
            ],
            options={
                'verbose_name': 'Phiếu Xuất',
                'verbose_name_plural': 'Phiếu Xuất',
            },
        ),
        migrations.CreateModel(
            name='PhieuXuatChiTiet',
            fields=[
                ('ma_ct_phieu_xuat', models.AutoField(primary_key=True, serialize=False)),
                ('so_luong', models.DecimalField(decimal_places=2, max_digits=10)),
                ('don_gia', models.DecimalField(decimal_places=2, max_digits=15)),
                ('ma_ong', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phieu_xuat_chi_tiet', to='inventory.ongnuoc')),
                ('ma_phieu_xuat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chi_tiet', to='inventory.phieuxuat')),
            ],
            options={
                'verbose_name': 'Chi Tiết Phiếu Xuất',
                'verbose_name_plural': 'Chi Tiết Phiếu Xuất',
            },
        ),
        migrations.CreateModel(
            name='PhieuNhapChiTiet',
            fields=[
                ('ma_ct_phieu_nhap', models.AutoField(primary_key=True, serialize=False)),
                ('so_luong', models.DecimalField(decimal_places=2, max_digits=10)),
                ('don_gia', models.DecimalField(decimal_places=2, max_digits=15)),
                ('ma_ong', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phieu_nhap_chi_tiet', to='inventory.ongnuoc')),
                ('ma_phieu_nhap', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chi_tiet', to='inventory.phieunhap')),
            ],
            options={
                'verbose_name': 'Chi Tiết Phiếu Nhập',
                'verbose_name_plural': 'Chi Tiết Phiếu Nhập',
            },
        ),
    ]
